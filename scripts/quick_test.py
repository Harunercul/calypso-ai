#!/usr/bin/env python3
"""
Quick Test Script
TÜBİTAK İP-2 AI Bot System

Sistemin çalıştığını hızlıca test etmek için script.

Usage:
    python scripts/quick_test.py
"""

import os
import sys

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Import test."""
    print("Testing imports...")

    try:
        from python_rl_server.agents import PPOAgent, RuleBasedAgent, BaseAgent
        print("  [OK] Agents module")
    except ImportError as e:
        print(f"  [FAIL] Agents module: {e}")
        return False

    try:
        from python_rl_server.environments import MockCombatEnv, ObservationBuilder
        print("  [OK] Environments module")
    except ImportError as e:
        print(f"  [FAIL] Environments module: {e}")
        return False

    try:
        from python_rl_server.training import RewardCalculator, TrainingCallback
        print("  [OK] Training module")
    except ImportError as e:
        print(f"  [FAIL] Training module: {e}")
        return False

    try:
        from python_rl_server.difficulty import DifficultyManager, PlayerPerformanceTracker
        print("  [OK] Difficulty module")
    except ImportError as e:
        print(f"  [FAIL] Difficulty module: {e}")
        return False

    try:
        from python_rl_server.server import BotAIServer
        print("  [OK] Server module")
    except ImportError as e:
        print(f"  [FAIL] Server module: {e}")
        return False

    try:
        from python_rl_server.utils import load_config, setup_logger
        print("  [OK] Utils module")
    except ImportError as e:
        print(f"  [FAIL] Utils module: {e}")
        return False

    return True


def test_mock_env():
    """Mock environment test."""
    print("\nTesting Mock Environment...")

    from python_rl_server.environments import MockCombatEnv

    env = MockCombatEnv(max_steps=100, num_enemies=3, difficulty=0.5)

    # Reset
    obs, info = env.reset()
    print(f"  Observation shape: {obs.shape}")
    assert obs.shape == (64,), "Observation should be 64-dim"
    print("  [OK] Reset works")

    # Step
    for _ in range(10):
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)

    print("  [OK] Step works")

    env.close()
    print("  [OK] Environment test passed")
    return True


def test_rule_based_agent():
    """Rule-based agent test."""
    print("\nTesting Rule-Based Agent...")

    from python_rl_server.agents import RuleBasedAgent
    from python_rl_server.environments import MockCombatEnv
    import numpy as np

    agent = RuleBasedAgent()
    env = MockCombatEnv()

    obs, _ = env.reset()

    # Aksiyon seç
    action, info = agent.select_action(obs, deterministic=True)
    print(f"  Action: {action} ({agent.get_action_name(action)})")
    print(f"  Utility scores: {len(info)} items")

    # 10 step çalıştır
    total_reward = 0
    for _ in range(10):
        obs, _ = env.reset()
        action, info = agent.select_action(obs)
        obs, reward, done, truncated, _ = env.step(action)
        total_reward += reward

    print(f"  [OK] Agent works, total reward: {total_reward:.2f}")

    env.close()
    return True


def test_ppo_agent():
    """PPO agent test."""
    print("\nTesting PPO Agent...")

    from python_rl_server.agents import PPOAgent
    from python_rl_server.environments import MockCombatEnv

    env = MockCombatEnv()
    agent = PPOAgent(verbose=0)

    # Initialize
    agent.initialize(env)
    print("  [OK] PPO initialized")

    # Select action
    obs, _ = env.reset()
    action, info = agent.select_action(obs, deterministic=True)
    print(f"  Action: {action}")
    print(f"  Value estimate: {info.get('value_estimate', 'N/A')}")
    print("  [OK] PPO action selection works")

    env.close()
    return True


def test_difficulty_manager():
    """Difficulty manager test."""
    print("\nTesting Difficulty Manager...")

    from python_rl_server.difficulty import DifficultyManager

    dm = DifficultyManager()
    dm.register_player("test_player")

    # Get difficulty
    diff = dm.get_current_difficulty("test_player")
    level = dm.get_difficulty_level("test_player")
    print(f"  Initial difficulty: {diff:.2f} (Level {level})")

    # Get params
    params = dm.get_bot_params("test_player")
    print(f"  Bot health: {params.health}")
    print(f"  Bot accuracy: {params.accuracy}")

    # Set difficulty
    dm.set_difficulty("test_player", 5)
    level = dm.get_difficulty_level("test_player")
    print(f"  After set to 5: Level {level}")

    print("  [OK] Difficulty manager works")
    return True


def test_reward_calculator():
    """Reward calculator test."""
    print("\nTesting Reward Calculator...")

    from python_rl_server.training import RewardCalculator

    calc = RewardCalculator()

    # Test events
    kill_reward = calc.calculate_reward("kill")
    print(f"  Kill reward: {kill_reward}")

    damage_reward = calc.calculate_reward("damage_dealt", 0.3)
    print(f"  Damage reward (30%): {damage_reward}")

    death_reward = calc.calculate_reward("death")
    print(f"  Death penalty: {death_reward}")

    stats = calc.get_episode_stats()
    print(f"  Episode stats: kills={stats['kills']}, deaths={stats['deaths']}")

    print("  [OK] Reward calculator works")
    return True


def run_quick_episode():
    """Hızlı bir episode çalıştır."""
    print("\nRunning quick episode...")

    from python_rl_server.agents import RuleBasedAgent
    from python_rl_server.environments import MockCombatEnv

    env = MockCombatEnv(render_mode="human", max_steps=50)
    agent = RuleBasedAgent()

    obs, _ = env.reset()
    total_reward = 0
    steps = 0

    print("\n--- Episode Start ---")
    while True:
        action, info = agent.select_action(obs, deterministic=True)
        obs, reward, done, truncated, ep_info = env.step(action)
        total_reward += reward
        steps += 1

        # Her 10 step'te render
        if steps % 10 == 0:
            env.render()

        if done or truncated:
            break

    print(f"\n--- Episode End ---")
    print(f"Steps: {steps}")
    print(f"Total Reward: {total_reward:.2f}")
    print(f"Kills: {ep_info.get('bot_kills', 0)}")
    print(f"Bot Health: {ep_info.get('bot_health', 0):.2f}")
    print(f"Enemies Alive: {ep_info.get('enemies_alive', 0)}")

    env.close()
    return True


def main():
    print("=" * 60)
    print("TÜBİTAK İP-2 AI Bot System - Quick Test")
    print("=" * 60)

    all_passed = True

    # Run tests
    all_passed &= test_imports()
    all_passed &= test_mock_env()
    all_passed &= test_rule_based_agent()
    all_passed &= test_ppo_agent()
    all_passed &= test_difficulty_manager()
    all_passed &= test_reward_calculator()

    # Quick episode
    print("\n" + "-" * 60)
    run_quick_episode()

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests PASSED!")
        print("System is ready for training and deployment.")
    else:
        print("Some tests FAILED!")
        print("Please check the errors above.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
