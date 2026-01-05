"""
Agent Tests
TÜBİTAK İP-2 AI Bot System
"""

import pytest
import numpy as np

from python_rl_server.agents import PPOAgent, RuleBasedAgent, BaseAgent
from python_rl_server.environments import MockCombatEnv


class TestRuleBasedAgent:
    """Rule-Based Agent testleri."""

    def test_initialization(self):
        """Agent oluşturma testi."""
        agent = RuleBasedAgent()
        assert agent.name == "RuleBasedAgent"
        assert agent.observation_dim == 64
        assert agent.action_dim == 9

    def test_action_selection(self):
        """Aksiyon seçimi testi."""
        agent = RuleBasedAgent()
        obs = np.random.rand(64).astype(np.float32)

        action, info = agent.select_action(obs, deterministic=True)

        assert isinstance(action, int)
        assert 0 <= action <= 8
        assert "utility_ATTACK" in info or "utility_IDLE" in info

    def test_stochastic_selection(self):
        """Stochastic aksiyon seçimi testi."""
        agent = RuleBasedAgent()
        obs = np.random.rand(64).astype(np.float32)

        actions = set()
        for _ in range(100):
            action, _ = agent.select_action(obs, deterministic=False)
            actions.add(action)

        # Stochastic modda farklı aksiyonlar seçilmeli
        assert len(actions) > 1

    def test_personality_parameters(self):
        """Personality parametreleri testi."""
        aggressive_agent = RuleBasedAgent(aggression=0.9, caution=0.1)
        cautious_agent = RuleBasedAgent(aggression=0.1, caution=0.9)

        # Düşman görünür durumda bir observation
        obs = np.zeros(64, dtype=np.float32)
        obs[0] = 0.8   # health
        obs[2] = 0.8   # ammo
        obs[16] = 0.3  # enemy distance (yakın)
        obs[19] = 1.0  # enemy visible
        obs[21] = 0.5  # threat level

        agg_action, agg_info = aggressive_agent.select_action(obs)
        caut_action, caut_info = cautious_agent.select_action(obs)

        # Aggressive agent'ın ATTACK utility'si daha yüksek olmalı
        assert agg_info.get("utility_ATTACK", 0) >= caut_info.get("utility_ATTACK", 0)


class TestPPOAgent:
    """PPO Agent testleri."""

    @pytest.fixture
    def env(self):
        """Test environment."""
        return MockCombatEnv(max_steps=100)

    @pytest.fixture
    def agent(self, env):
        """Initialized PPO agent."""
        agent = PPOAgent(verbose=0)
        agent.initialize(env)
        return agent

    def test_initialization(self, agent):
        """PPO initialization testi."""
        assert agent.name == "PPOAgent"
        assert agent.model is not None

    def test_action_selection(self, agent):
        """Aksiyon seçimi testi."""
        obs = np.random.rand(64).astype(np.float32)

        action, info = agent.select_action(obs, deterministic=True)

        assert isinstance(action, int)
        assert 0 <= action <= 8
        assert "value_estimate" in info

    def test_save_load(self, agent, env, tmp_path):
        """Model save/load testi."""
        save_path = str(tmp_path / "test_model")

        # Save
        agent.save(save_path)

        # Load
        new_agent = PPOAgent(verbose=0)
        new_agent.load(save_path, env=env)

        assert new_agent.model is not None


class TestAgentInEnvironment:
    """Agent-Environment entegrasyon testleri."""

    def test_rule_based_episode(self):
        """Rule-based agent ile tam episode."""
        env = MockCombatEnv(max_steps=100)
        agent = RuleBasedAgent()

        obs, _ = env.reset()
        total_reward = 0
        steps = 0

        while True:
            action, _ = agent.select_action(obs)
            obs, reward, done, truncated, _ = env.step(action)
            total_reward += reward
            steps += 1

            if done or truncated:
                break

        assert steps > 0
        assert steps <= 100
        env.close()

    def test_ppo_episode(self):
        """PPO agent ile tam episode."""
        env = MockCombatEnv(max_steps=100)
        agent = PPOAgent(verbose=0)
        agent.initialize(env)

        obs, _ = env.reset()
        total_reward = 0
        steps = 0

        while True:
            action, _ = agent.select_action(obs)
            obs, reward, done, truncated, _ = env.step(action)
            total_reward += reward
            steps += 1

            if done or truncated:
                break

        assert steps > 0
        env.close()
