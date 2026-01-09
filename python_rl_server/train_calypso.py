#!/usr/bin/env python3
"""
CALYPSO AI Bot Training Script
TÜBİTAK İP-2 AI Bot System

Tier bazlı düşman sistemine karşı PPO eğitimi.
"""

import os
import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    EvalCallback,
    CheckpointCallback,
    CallbackList
)
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed

from environments import CalypsoMockEnv, EnemyTier, AreaType


def make_env(tier: int, alarm: int, area: int, rank: int = 0, seed: int = 0):
    """Environment factory for vectorized envs."""
    def _init():
        env = CalypsoMockEnv(
            initial_tier=tier,
            alarm_level=alarm,
            area_type=area,
            enable_boss=(tier >= 2 and rank == 0),
            player_skill=0.5
        )
        env.reset(seed=seed + rank)
        return env
    set_random_seed(seed)
    return _init


def train(args):
    """Ana eğitim fonksiyonu."""
    print("=" * 60)
    print("CALYPSO AI Bot Training")
    print("=" * 60)
    print(f"Tier: {args.tier}")
    print(f"Alarm Level: {args.alarm}")
    print(f"Area Type: {AreaType(args.area).name}")
    print(f"Total Timesteps: {args.timesteps:,}")
    print(f"Num Environments: {args.n_envs}")
    print("=" * 60)

    # Model kayıt dizini
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = Path(f"models/calypso_tier{args.tier}_{timestamp}")
    model_dir.mkdir(parents=True, exist_ok=True)
    log_dir = model_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    # Vectorized environment
    if args.n_envs > 1:
        env = SubprocVecEnv([
            make_env(args.tier, args.alarm, args.area, i, args.seed)
            for i in range(args.n_envs)
        ])
    else:
        env = DummyVecEnv([
            make_env(args.tier, args.alarm, args.area, 0, args.seed)
        ])

    # Eval environment
    eval_env = DummyVecEnv([
        make_env(args.tier, args.alarm, args.area, 0, args.seed + 100)
    ])

    # PPO Model
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=str(log_dir),
        device="auto"
    )

    # Callbacks
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(model_dir / "best"),
        log_path=str(log_dir),
        eval_freq=10000,
        deterministic=True,
        render=False
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=50000,
        save_path=str(model_dir / "checkpoints"),
        name_prefix="calypso_ppo"
    )

    callbacks = CallbackList([eval_callback, checkpoint_callback])

    # Training
    print(f"\nTraining started. Logs: {log_dir}")
    print("Run 'tensorboard --logdir logs' to monitor training.\n")

    model.learn(
        total_timesteps=args.timesteps,
        callback=callbacks,
        progress_bar=True
    )

    # Final save
    final_path = model_dir / "final_model"
    model.save(str(final_path))
    print(f"\nTraining complete! Model saved to: {final_path}")

    # Quick evaluation
    print("\nRunning final evaluation...")
    eval_rewards = []
    for _ in range(10):
        obs = eval_env.reset()
        total_reward = 0
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = eval_env.step(action)
            total_reward += reward[0]
        eval_rewards.append(total_reward)

    print(f"Mean Reward: {np.mean(eval_rewards):.2f} +/- {np.std(eval_rewards):.2f}")

    env.close()
    eval_env.close()

    return model


def curriculum_train(args):
    """
    Curriculum Learning - Tier 1'den başlayıp zorlaştır.

    Eğitim sırası:
    1. Tier 1 (kolay) - Temel davranışları öğren
    2. Tier 2 (orta) - Taktiksel davranışları öğren
    3. Tier 2 + Boss - Boss mekaniklerini öğren
    """
    print("=" * 60)
    print("CALYPSO Curriculum Learning")
    print("=" * 60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(f"models/calypso_curriculum_{timestamp}")
    base_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1: Tier 1
    print("\n[Phase 1/3] Tier 1 Training...")
    env1 = DummyVecEnv([make_env(1, 1, 1, 0, args.seed)])

    model = PPO(
        "MlpPolicy",
        env1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        verbose=1,
        tensorboard_log=str(base_dir / "logs")
    )

    model.learn(total_timesteps=args.timesteps // 3, progress_bar=True)
    model.save(str(base_dir / "phase1_tier1"))
    env1.close()

    # Phase 2: Tier 2
    print("\n[Phase 2/3] Tier 2 Training...")
    env2 = DummyVecEnv([make_env(2, 2, 1, 0, args.seed)])
    model.set_env(env2)

    model.learn(total_timesteps=args.timesteps // 3, progress_bar=True)
    model.save(str(base_dir / "phase2_tier2"))
    env2.close()

    # Phase 3: Tier 2 + Boss
    print("\n[Phase 3/3] Boss Training...")
    env3 = DummyVecEnv([lambda: CalypsoMockEnv(
        initial_tier=2, alarm_level=3, area_type=2, enable_boss=True
    )])
    model.set_env(env3)

    model.learn(total_timesteps=args.timesteps // 3, progress_bar=True)
    model.save(str(base_dir / "phase3_boss"))
    env3.close()

    # Final model
    model.save(str(base_dir / "final_curriculum"))
    print(f"\nCurriculum training complete! Models saved to: {base_dir}")

    return model


def evaluate(args):
    """Eğitilmiş modeli değerlendir."""
    print("=" * 60)
    print("CALYPSO Model Evaluation")
    print("=" * 60)

    model = PPO.load(args.model_path)

    env = CalypsoMockEnv(
        initial_tier=args.tier,
        alarm_level=args.alarm,
        area_type=args.area,
        enable_boss=args.enable_boss,
        render_mode="human" if args.render else None
    )

    rewards = []
    kills = []
    survivals = []

    for episode in range(args.episodes):
        obs, info = env.reset()
        total_reward = 0
        done = False
        steps = 0

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, term, trunc, info = env.step(action)
            total_reward += reward
            done = term or trunc
            steps += 1

            if args.render:
                env.render()

        rewards.append(total_reward)
        kills.append(info['bot_kills'])
        survivals.append(1 if info['bot_health'] > 0 else 0)

        print(f"Episode {episode + 1}: Reward={total_reward:.2f}, "
              f"Kills={info['bot_kills']}, Survived={info['bot_health'] > 0}")

    print("\n" + "=" * 60)
    print(f"Mean Reward: {np.mean(rewards):.2f} +/- {np.std(rewards):.2f}")
    print(f"Mean Kills: {np.mean(kills):.2f}")
    print(f"Survival Rate: {np.mean(survivals) * 100:.1f}%")
    print("=" * 60)

    env.close()


def main():
    parser = argparse.ArgumentParser(description="CALYPSO AI Bot Training")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train a model")
    train_parser.add_argument("--tier", type=int, default=1, choices=[1, 2],
                             help="Enemy tier (1=easy, 2=medium)")
    train_parser.add_argument("--alarm", type=int, default=1, choices=[1, 2, 3],
                             help="Alarm level")
    train_parser.add_argument("--area", type=int, default=1, choices=[0, 1, 2],
                             help="Area type (0=narrow, 1=medium, 2=wide)")
    train_parser.add_argument("--timesteps", type=int, default=100000,
                             help="Total timesteps")
    train_parser.add_argument("--n-envs", type=int, default=4,
                             help="Number of parallel environments")
    train_parser.add_argument("--seed", type=int, default=42,
                             help="Random seed")

    # Curriculum command
    curr_parser = subparsers.add_parser("curriculum", help="Curriculum learning")
    curr_parser.add_argument("--timesteps", type=int, default=300000,
                            help="Total timesteps (split across phases)")
    curr_parser.add_argument("--seed", type=int, default=42,
                            help="Random seed")

    # Evaluate command
    eval_parser = subparsers.add_parser("eval", help="Evaluate a model")
    eval_parser.add_argument("model_path", type=str, help="Path to model file")
    eval_parser.add_argument("--tier", type=int, default=1, choices=[1, 2])
    eval_parser.add_argument("--alarm", type=int, default=1, choices=[1, 2, 3])
    eval_parser.add_argument("--area", type=int, default=1, choices=[0, 1, 2])
    eval_parser.add_argument("--enable-boss", action="store_true")
    eval_parser.add_argument("--episodes", type=int, default=10)
    eval_parser.add_argument("--render", action="store_true")

    args = parser.parse_args()

    if args.command == "train":
        train(args)
    elif args.command == "curriculum":
        curriculum_train(args)
    elif args.command == "eval":
        evaluate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
