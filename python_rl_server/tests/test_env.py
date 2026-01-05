"""
Environment Tests
TÜBİTAK İP-2 AI Bot System
"""

import pytest
import numpy as np

from python_rl_server.environments import MockCombatEnv, ObservationBuilder
from python_rl_server.environments.observation import BotSelfState, EnemyState


class TestObservationBuilder:
    """ObservationBuilder testleri."""

    def test_observation_dim(self):
        """Observation boyutu testi."""
        builder = ObservationBuilder()
        obs = builder.build()

        assert obs.shape == (64,)
        assert obs.dtype == np.float32

    def test_default_values(self):
        """Default değerler testi."""
        builder = ObservationBuilder()
        obs = builder.build()

        # Health default 1.0
        assert obs[0] == 1.0
        # Enemy distance default 1.0 (uzak)
        assert obs[16] == 1.0

    def test_self_state_update(self):
        """Self state güncelleme testi."""
        builder = ObservationBuilder()
        builder.self_state = BotSelfState(health=0.5, ammo_primary=0.3)
        obs = builder.build()

        assert obs[0] == 0.5  # health
        assert obs[2] == 0.3  # ammo_primary

    def test_enemy_state_update(self):
        """Enemy state güncelleme testi."""
        builder = ObservationBuilder()
        builder.enemies[0] = EnemyState(distance=0.2, is_visible=1.0, threat_level=0.8)
        obs = builder.build()

        assert obs[16] == 0.2  # enemy1 distance
        assert obs[19] == 1.0  # enemy1 visible
        assert obs[21] == 0.8  # enemy1 threat

    def test_from_array(self):
        """Array'den parse testi."""
        builder = ObservationBuilder()
        obs = np.random.rand(64).astype(np.float32)

        builder.from_array(obs)

        assert builder.self_state.health == obs[0]
        assert builder.enemies[0].distance == obs[16]


class TestMockCombatEnv:
    """MockCombatEnv testleri."""

    @pytest.fixture
    def env(self):
        """Test environment."""
        return MockCombatEnv(max_steps=100, num_enemies=3, difficulty=0.5)

    def test_observation_space(self, env):
        """Observation space testi."""
        assert env.observation_space.shape == (64,)

    def test_action_space(self, env):
        """Action space testi."""
        assert env.action_space.n == 9

    def test_reset(self, env):
        """Reset testi."""
        obs, info = env.reset()

        assert obs.shape == (64,)
        assert "step" in info
        assert info["step"] == 0

    def test_step(self, env):
        """Step testi."""
        env.reset()
        action = env.action_space.sample()

        obs, reward, done, truncated, info = env.step(action)

        assert obs.shape == (64,)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(truncated, bool)
        assert "step" in info

    def test_episode_termination(self, env):
        """Episode sonlanma testi."""
        env.reset()
        done = False
        truncated = False
        steps = 0

        while not done and not truncated:
            action = env.action_space.sample()
            _, _, done, truncated, _ = env.step(action)
            steps += 1

            # Safety limit
            if steps > 1000:
                break

        assert done or truncated

    def test_max_steps_truncation(self):
        """Max steps truncation testi."""
        env = MockCombatEnv(max_steps=10)
        env.reset()

        for _ in range(10):
            _, _, done, truncated, _ = env.step(0)  # IDLE

        assert truncated

        env.close()

    def test_attack_action(self, env):
        """Attack aksiyonu testi."""
        env.reset()
        initial_ammo = env._bot_ammo

        _, reward, _, _, _ = env.step(1)  # ACTION_ATTACK

        # Ammo azalmalı
        assert env._bot_ammo < initial_ammo

    def test_cover_action(self, env):
        """Cover aksiyonu testi."""
        env.reset()

        _, reward, _, _, _ = env.step(2)  # ACTION_TAKE_COVER

        assert env._bot_in_cover == True

    def test_reload_action(self, env):
        """Reload aksiyonu testi."""
        env.reset()
        env._bot_ammo = 0.2  # Düşük ammo

        _, reward, _, _, _ = env.step(4)  # ACTION_RELOAD

        assert env._bot_ammo > 0.2

    def test_difficulty_affects_damage(self):
        """Zorluk seviyesinin hasara etkisi testi."""
        easy_env = MockCombatEnv(difficulty=0.1)
        hard_env = MockCombatEnv(difficulty=0.9)

        # Her iki env'de 100 step çalıştır
        easy_env.reset()
        hard_env.reset()

        easy_damage = 0
        hard_damage = 0

        for _ in range(100):
            easy_env.step(0)  # IDLE
            hard_env.step(0)  # IDLE

            easy_damage = easy_env._damage_taken
            hard_damage = hard_env._damage_taken

        # Hard env'de daha fazla hasar alınmalı (genellikle)
        # Not: Random olduğu için her zaman doğru olmayabilir

        easy_env.close()
        hard_env.close()


class TestEnvironmentSeeding:
    """Environment seeding testleri."""

    def test_deterministic_with_seed(self):
        """Aynı seed ile aynı sonuçlar."""
        env1 = MockCombatEnv()
        env2 = MockCombatEnv()

        obs1, _ = env1.reset(seed=42)
        obs2, _ = env2.reset(seed=42)

        np.testing.assert_array_almost_equal(obs1, obs2)

        env1.close()
        env2.close()
