#!/usr/bin/env python3
"""
Evaluation Script
TÜBİTAK İP-2 AI Bot System

Eğitilmiş model'i evaluate etmek için script.

Usage:
    python scripts/evaluate.py --model ./models/ppo_best.zip --episodes 100
    python scripts/evaluate.py --rule-based --episodes 100
    python scripts/evaluate.py --compare --model ./models/ppo_best.zip --episodes 50
"""

import argparse
import os
import sys
from typing import Dict, List

import numpy as np

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python_rl_server.agents import PPOAgent, RuleBasedAgent
from python_rl_server.environments import MockCombatEnv


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate Bot Agent")

    parser.add_argument(
        "--model", type=str, default=None,
        help="Path to trained PPO model"
    )
    parser.add_argument(
        "--rule-based", action="store_true",
        help="Evaluate rule-based agent"
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="Compare PPO vs Rule-Based"
    )
    parser.add_argument(
        "--episodes", type=int, default=100,
        help="Number of evaluation episodes"
    )
    parser.add_argument(
        "--difficulty", type=float, default=0.5,
        help="Environment difficulty (0-1)"
    )
    parser.add_argument(
        "--render", action="store_true",
        help="Render environment (text mode)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed"
    )

    return parser.parse_args()


def evaluate_agent(
    agent,
    env,
    n_episodes: int,
    render: bool = False,
    verbose: bool = False
) -> Dict:
    """
    Agent'ı evaluate et.

    Returns:
        Evaluation metrics dictionary
    """
    episode_rewards = []
    episode_lengths = []
    episode_kills = []
    episode_deaths = []
    win_count = 0

    for ep in range(n_episodes):
        obs, info = env.reset()
        done = False
        truncated = False
        episode_reward = 0.0
        episode_length = 0

        while not done and not truncated:
            action, action_info = agent.select_action(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1

            if render:
                env.render()

        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        episode_kills.append(info.get("bot_kills", 0))

        # Win = tüm düşmanlar öldü
        if info.get("enemies_alive", 1) == 0:
            win_count += 1

        if info.get("bot_health", 1) <= 0:
            episode_deaths.append(1)
        else:
            episode_deaths.append(0)

        if verbose:
            print(f"Episode {ep + 1}/{n_episodes}: "
                  f"Reward={episode_reward:.2f}, "
                  f"Length={episode_length}, "
                  f"Kills={info.get('bot_kills', 0)}, "
                  f"Win={'Yes' if info.get('enemies_alive', 1) == 0 else 'No'}")

    # Metrics hesapla
    metrics = {
        "mean_reward": np.mean(episode_rewards),
        "std_reward": np.std(episode_rewards),
        "min_reward": np.min(episode_rewards),
        "max_reward": np.max(episode_rewards),
        "mean_length": np.mean(episode_lengths),
        "mean_kills": np.mean(episode_kills),
        "total_kills": sum(episode_kills),
        "total_deaths": sum(episode_deaths),
        "win_rate": win_count / n_episodes,
        "survival_rate": 1 - (sum(episode_deaths) / n_episodes)
    }

    return metrics


def print_metrics(name: str, metrics: Dict):
    """Metrikleri yazdır."""
    print(f"\n{'=' * 50}")
    print(f"  {name} Results")
    print(f"{'=' * 50}")
    print(f"  Episodes:       {metrics.get('episodes', 'N/A')}")
    print(f"  Mean Reward:    {metrics['mean_reward']:.2f} (+/- {metrics['std_reward']:.2f})")
    print(f"  Min/Max Reward: {metrics['min_reward']:.2f} / {metrics['max_reward']:.2f}")
    print(f"  Mean Length:    {metrics['mean_length']:.1f}")
    print(f"  Mean Kills:     {metrics['mean_kills']:.2f}")
    print(f"  Win Rate:       {metrics['win_rate'] * 100:.1f}%")
    print(f"  Survival Rate:  {metrics['survival_rate'] * 100:.1f}%")
    print(f"{'=' * 50}")


def main():
    args = parse_args()

    print(f"=" * 60)
    print(f"TÜBİTAK İP-2 Bot Agent Evaluation")
    print(f"=" * 60)
    print(f"Episodes: {args.episodes}")
    print(f"Difficulty: {args.difficulty}")
    print(f"Seed: {args.seed}")
    print("-" * 60)

    # Environment oluştur
    env = MockCombatEnv(
        max_steps=1000,
        num_enemies=3,
        difficulty=args.difficulty
    )

    np.random.seed(args.seed)

    if args.compare:
        # PPO vs Rule-Based karşılaştırma
        print("\nComparing PPO vs Rule-Based agents...")

        # PPO Agent
        ppo_agent = PPOAgent(verbose=0)
        if args.model and os.path.exists(args.model):
            ppo_agent.initialize(env)
            ppo_agent.load(args.model)
            print(f"Loaded PPO model: {args.model}")
        else:
            print("WARNING: No PPO model specified. Using untrained agent.")
            ppo_agent.initialize(env)

        # Rule-Based Agent
        rule_agent = RuleBasedAgent(
            aggression=0.5,
            caution=0.5,
            team_focus=0.5
        )

        # Evaluate both
        print("\nEvaluating PPO Agent...")
        ppo_metrics = evaluate_agent(
            ppo_agent, env, args.episodes,
            render=args.render, verbose=args.verbose
        )
        ppo_metrics["episodes"] = args.episodes

        print("\nEvaluating Rule-Based Agent...")
        rule_metrics = evaluate_agent(
            rule_agent, env, args.episodes,
            render=args.render, verbose=args.verbose
        )
        rule_metrics["episodes"] = args.episodes

        # Print results
        print_metrics("PPO Agent", ppo_metrics)
        print_metrics("Rule-Based Agent", rule_metrics)

        # Comparison
        print(f"\n{'=' * 50}")
        print(f"  Comparison Summary")
        print(f"{'=' * 50}")

        reward_diff = ppo_metrics["mean_reward"] - rule_metrics["mean_reward"]
        win_diff = (ppo_metrics["win_rate"] - rule_metrics["win_rate"]) * 100

        print(f"  Reward Difference:  {reward_diff:+.2f} ({'PPO' if reward_diff > 0 else 'Rule-Based'} better)")
        print(f"  Win Rate Diff:      {win_diff:+.1f}% ({'PPO' if win_diff > 0 else 'Rule-Based'} better)")
        print(f"{'=' * 50}")

    else:
        # Single agent evaluation
        if args.rule_based:
            print("\nEvaluating Rule-Based Agent...")
            agent = RuleBasedAgent(
                aggression=0.5,
                caution=0.5,
                team_focus=0.5
            )
            agent_name = "Rule-Based Agent"
        else:
            print("\nEvaluating PPO Agent...")
            agent = PPOAgent(verbose=0)

            if args.model and os.path.exists(args.model):
                agent.initialize(env)
                agent.load(args.model)
                print(f"Loaded model: {args.model}")
            else:
                print("WARNING: No model specified. Using untrained agent.")
                agent.initialize(env)

            agent_name = "PPO Agent"

        # Evaluate
        metrics = evaluate_agent(
            agent, env, args.episodes,
            render=args.render, verbose=args.verbose
        )
        metrics["episodes"] = args.episodes

        # Print results
        print_metrics(agent_name, metrics)

    # Cleanup
    env.close()
    print("\nEvaluation completed!")


if __name__ == "__main__":
    main()
