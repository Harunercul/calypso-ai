#!/usr/bin/env python3
"""
Training Script
TÜBİTAK İP-2 AI Bot System

PPO Agent'ı eğitmek için ana script.

Usage:
    python scripts/train_agent.py --env mock --timesteps 100000
    python scripts/train_agent.py --config configs/training_config.yaml
"""

import argparse
import os
import sys
from datetime import datetime

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python_rl_server.agents import PPOAgent
from python_rl_server.environments import MockCombatEnv
from python_rl_server.training import TrainingCallback, EvaluationCallback
from python_rl_server.utils import load_config, setup_logger, TrainingLogger


def parse_args():
    parser = argparse.ArgumentParser(description="Train PPO Agent")

    parser.add_argument(
        "--env", type=str, default="mock",
        choices=["mock"],
        help="Environment type"
    )
    parser.add_argument(
        "--timesteps", type=int, default=100000,
        help="Total training timesteps"
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to training config YAML"
    )
    parser.add_argument(
        "--save-dir", type=str, default="./models",
        help="Model save directory"
    )
    parser.add_argument(
        "--log-dir", type=str, default="./logs",
        help="Log directory"
    )
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Path to model to resume training from"
    )
    parser.add_argument(
        "--eval-freq", type=int, default=10000,
        help="Evaluation frequency (steps)"
    )
    parser.add_argument(
        "--difficulty", type=float, default=0.5,
        help="Environment difficulty (0-1)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed"
    )
    parser.add_argument(
        "--verbose", type=int, default=1,
        help="Verbosity level"
    )

    return parser.parse_args()


def create_env(env_type: str, difficulty: float, seed: int):
    """Environment oluştur."""
    if env_type == "mock":
        return MockCombatEnv(
            max_steps=1000,
            num_enemies=3,
            difficulty=difficulty
        )
    else:
        raise ValueError(f"Unknown environment: {env_type}")


def main():
    args = parse_args()

    # Experiment ismi
    experiment_name = datetime.now().strftime("ppo_%Y%m%d_%H%M%S")

    # Logger setup
    logger = TrainingLogger(
        log_dir=args.log_dir,
        experiment_name=experiment_name
    )

    print(f"=" * 60)
    print(f"TÜBİTAK İP-2 AI Bot Training")
    print(f"=" * 60)
    print(f"Experiment: {experiment_name}")
    print(f"Log dir: {logger.get_log_dir()}")
    print(f"=" * 60)

    # Config yükle
    if args.config:
        config = load_config(args.config)
        ppo_config = config.get("ppo", {})
        training_config = config.get("training", {})

        # Args'tan override
        timesteps = args.timesteps or training_config.get("total_timesteps", 100000)
    else:
        ppo_config = {}
        timesteps = args.timesteps

    # Hyperparametreler
    hyperparams = {
        "env_type": args.env,
        "total_timesteps": timesteps,
        "difficulty": args.difficulty,
        "seed": args.seed,
        **ppo_config
    }
    logger.log_hyperparams(hyperparams)

    print(f"\nHyperparameters:")
    for k, v in hyperparams.items():
        print(f"  {k}: {v}")
    print()

    # Environment oluştur
    print("Creating environment...")
    env = create_env(args.env, args.difficulty, args.seed)
    eval_env = create_env(args.env, args.difficulty, args.seed + 1)

    # Agent oluştur
    print("Creating PPO agent...")
    agent = PPOAgent(
        name="PPO_CALYPSO",
        learning_rate=ppo_config.get("learning_rate", 3e-4),
        n_steps=ppo_config.get("n_steps", 2048),
        batch_size=ppo_config.get("batch_size", 64),
        n_epochs=ppo_config.get("n_epochs", 10),
        gamma=ppo_config.get("gamma", 0.99),
        verbose=args.verbose
    )

    # Agent'ı initialize et
    agent.initialize(env)

    # Resume
    if args.resume and os.path.exists(args.resume):
        print(f"Resuming from: {args.resume}")
        agent.load(args.resume, env=env)

    # Callbacks
    checkpoint_dir = os.path.join(args.save_dir, experiment_name)
    os.makedirs(checkpoint_dir, exist_ok=True)

    callbacks = [
        TrainingCallback(
            save_freq=args.eval_freq,
            save_path=checkpoint_dir,
            name_prefix="ppo_bot",
            verbose=args.verbose
        ),
        EvaluationCallback(
            eval_env=eval_env,
            eval_freq=args.eval_freq,
            n_eval_episodes=5,
            verbose=args.verbose
        )
    ]

    # Training
    print(f"\nStarting training for {timesteps} timesteps...")
    print(f"Checkpoints will be saved to: {checkpoint_dir}")
    print("-" * 60)

    try:
        agent.train(
            total_timesteps=timesteps,
            callback=callbacks,
            log_interval=10
        )
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")

    # Final save
    final_path = os.path.join(checkpoint_dir, "ppo_final")
    agent.save(final_path)
    print(f"\nFinal model saved to: {final_path}")

    # Cleanup
    env.close()
    eval_env.close()

    print("\n" + "=" * 60)
    print("Training completed!")
    print(f"Models saved to: {checkpoint_dir}")
    print(f"Logs saved to: {logger.get_log_dir()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
