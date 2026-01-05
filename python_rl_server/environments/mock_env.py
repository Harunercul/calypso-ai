"""
Mock Combat Environment - Unreal Engine olmadan test için
TÜBİTAK İP-2 AI Bot System

Bu environment Unreal Engine olmadan agent'ları test etmek için kullanılır.
Basitleştirilmiş bir savaş simülasyonu sağlar.
"""

from typing import Any, Dict, Optional, Tuple
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from .observation import ObservationBuilder, BotSelfState, EnemyState


class MockCombatEnv(gym.Env):
    """
    Mock Combat Environment.

    Basit bir TPS savaş ortamı simülasyonu.
    Agent'ların temel davranışlarını test etmek için kullanılır.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    # Action constants
    ACTION_IDLE = 0
    ACTION_ATTACK = 1
    ACTION_TAKE_COVER = 2
    ACTION_FLEE = 3
    ACTION_RELOAD = 4
    ACTION_PATROL = 5
    ACTION_INVESTIGATE = 6
    ACTION_SUPPORT = 7
    ACTION_FLANK = 8

    def __init__(
        self,
        render_mode: Optional[str] = None,
        max_steps: int = 1000,
        num_enemies: int = 3,
        difficulty: float = 0.5
    ):
        """
        Args:
            render_mode: "human" veya "rgb_array"
            max_steps: Episode başına maksimum step
            num_enemies: Düşman sayısı
            difficulty: Zorluk seviyesi (0-1)
        """
        super().__init__()

        self.render_mode = render_mode
        self.max_steps = max_steps
        self.num_enemies = num_enemies
        self.difficulty = difficulty

        # Observation ve Action spaces
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(64,),
            dtype=np.float32
        )

        self.action_space = spaces.Discrete(9)

        # State
        self._obs_builder = ObservationBuilder()
        self._step_count = 0
        self._total_reward = 0.0

        # Bot state
        self._bot_health = 1.0
        self._bot_ammo = 1.0
        self._bot_position = np.array([0.5, 0.5])
        self._bot_in_cover = False
        self._bot_kills = 0

        # Enemy states
        self._enemies = []
        self._enemies_alive = []

        # Combat stats
        self._damage_dealt = 0.0
        self._damage_taken = 0.0

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict]:
        """Environment'ı sıfırla."""
        super().reset(seed=seed)

        self._step_count = 0
        self._total_reward = 0.0

        # Bot reset
        self._bot_health = 1.0
        self._bot_ammo = 1.0
        self._bot_position = np.array([0.5, 0.5])
        self._bot_in_cover = False
        self._bot_kills = 0
        self._damage_dealt = 0.0
        self._damage_taken = 0.0

        # Spawn enemies
        self._enemies = []
        self._enemies_alive = []
        for i in range(self.num_enemies):
            enemy = {
                "position": np.array([
                    self.np_random.uniform(0.2, 0.8),
                    self.np_random.uniform(0.2, 0.8)
                ]),
                "health": 1.0,
                "in_cover": self.np_random.random() < 0.3,
                "aggressive": self.np_random.random() < self.difficulty
            }
            self._enemies.append(enemy)
            self._enemies_alive.append(True)

        obs = self._get_observation()
        info = self._get_info()

        return obs, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Bir step simüle et.

        Args:
            action: Seçilen aksiyon (0-8)

        Returns:
            observation, reward, terminated, truncated, info
        """
        self._step_count += 1
        reward = 0.0

        # Action'a göre işlem
        if action == self.ACTION_IDLE:
            reward += 0.0
            # Idle - survival bonus
            reward += 0.01

        elif action == self.ACTION_ATTACK:
            reward += self._do_attack()

        elif action == self.ACTION_TAKE_COVER:
            reward += self._do_take_cover()

        elif action == self.ACTION_FLEE:
            reward += self._do_flee()

        elif action == self.ACTION_RELOAD:
            reward += self._do_reload()

        elif action == self.ACTION_PATROL:
            reward += self._do_patrol()

        elif action == self.ACTION_INVESTIGATE:
            reward += self._do_investigate()

        elif action == self.ACTION_SUPPORT:
            reward += self._do_support()

        elif action == self.ACTION_FLANK:
            reward += self._do_flank()

        # Düşman aksiyonları
        self._enemy_actions()

        # Survival bonus
        if self._bot_health > 0:
            reward += 0.01

        self._total_reward += reward

        # Terminal conditions
        terminated = False
        truncated = False

        # Bot öldü
        if self._bot_health <= 0:
            terminated = True
            reward -= 10.0

        # Tüm düşmanlar öldü
        if not any(self._enemies_alive):
            terminated = True
            reward += 20.0  # Win bonus

        # Max step aşıldı
        if self._step_count >= self.max_steps:
            truncated = True

        obs = self._get_observation()
        info = self._get_info()

        return obs, reward, terminated, truncated, info

    def _do_attack(self) -> float:
        """Saldırı aksiyonu."""
        reward = 0.0

        if self._bot_ammo <= 0:
            return -0.1  # Mermi yok penalty

        self._bot_ammo -= 0.1

        # En yakın görünür düşmanı bul
        target_idx = self._find_nearest_visible_enemy()

        if target_idx is not None:
            enemy = self._enemies[target_idx]

            # İsabet şansı
            distance = np.linalg.norm(enemy["position"] - self._bot_position)
            hit_chance = max(0.3, 1.0 - distance)

            if enemy["in_cover"]:
                hit_chance *= 0.5

            if self.np_random.random() < hit_chance:
                damage = 0.3
                enemy["health"] -= damage
                self._damage_dealt += damage
                reward += 1.0  # Hit reward

                if enemy["health"] <= 0:
                    self._enemies_alive[target_idx] = False
                    self._bot_kills += 1
                    reward += 10.0  # Kill reward
        else:
            reward -= 0.05  # Hedef yok penalty

        return reward

    def _do_take_cover(self) -> float:
        """Siper al."""
        if self._bot_in_cover:
            return -0.01  # Zaten siperde

        self._bot_in_cover = True
        return 0.5  # Cover bonus

    def _do_flee(self) -> float:
        """Kaç."""
        # Rastgele yönde hareket
        direction = self.np_random.uniform(-1, 1, 2)
        direction = direction / (np.linalg.norm(direction) + 1e-8)

        self._bot_position += direction * 0.1
        self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
        self._bot_in_cover = False

        # Düşmanlardan uzaklaştıysa bonus
        if self._bot_health < 0.3:
            return 0.3
        return 0.0

    def _do_reload(self) -> float:
        """Mermi doldur."""
        if self._bot_ammo >= 1.0:
            return -0.05  # Zaten dolu

        self._bot_ammo = min(1.0, self._bot_ammo + 0.5)

        if self._bot_in_cover:
            return 0.2  # Siperde reload bonus
        return 0.1

    def _do_patrol(self) -> float:
        """Devriye."""
        direction = self.np_random.uniform(-1, 1, 2)
        direction = direction / (np.linalg.norm(direction) + 1e-8)

        self._bot_position += direction * 0.05
        self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
        self._bot_in_cover = False

        return 0.02

    def _do_investigate(self) -> float:
        """Araştır."""
        # En yakın düşmana doğru hareket
        nearest_idx = self._find_nearest_enemy()
        if nearest_idx is not None:
            enemy = self._enemies[nearest_idx]
            direction = enemy["position"] - self._bot_position
            direction = direction / (np.linalg.norm(direction) + 1e-8)

            self._bot_position += direction * 0.03
            self._bot_position = np.clip(self._bot_position, 0.0, 1.0)

        self._bot_in_cover = False
        return 0.05

    def _do_support(self) -> float:
        """Takım desteği (mock'ta sadece pozisyon değişikliği)."""
        self._bot_position += self.np_random.uniform(-0.05, 0.05, 2)
        self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
        return 0.1

    def _do_flank(self) -> float:
        """Yan atak."""
        nearest_idx = self._find_nearest_visible_enemy()
        if nearest_idx is not None:
            enemy = self._enemies[nearest_idx]

            # Yan yönde hareket
            direction = enemy["position"] - self._bot_position
            perpendicular = np.array([-direction[1], direction[0]])
            perpendicular = perpendicular / (np.linalg.norm(perpendicular) + 1e-8)

            self._bot_position += perpendicular * 0.1
            self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
            self._bot_in_cover = False
            return 0.3

        return 0.0

    def _enemy_actions(self) -> None:
        """Düşman aksiyonları simüle et."""
        for i, (enemy, alive) in enumerate(zip(self._enemies, self._enemies_alive)):
            if not alive:
                continue

            # Agresif düşman saldırır
            if enemy["aggressive"] and self.np_random.random() < self.difficulty:
                # Saldırı
                distance = np.linalg.norm(enemy["position"] - self._bot_position)
                hit_chance = max(0.1, 0.5 - distance) * self.difficulty

                if self._bot_in_cover:
                    hit_chance *= 0.3

                if self.np_random.random() < hit_chance:
                    damage = 0.1 * self.difficulty
                    self._bot_health -= damage
                    self._damage_taken += damage

            # Rastgele hareket
            if self.np_random.random() < 0.3:
                enemy["position"] += self.np_random.uniform(-0.05, 0.05, 2)
                enemy["position"] = np.clip(enemy["position"], 0.0, 1.0)

    def _find_nearest_enemy(self) -> Optional[int]:
        """En yakın düşmanı bul."""
        min_dist = float('inf')
        nearest_idx = None

        for i, (enemy, alive) in enumerate(zip(self._enemies, self._enemies_alive)):
            if not alive:
                continue

            dist = np.linalg.norm(enemy["position"] - self._bot_position)
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i

        return nearest_idx

    def _find_nearest_visible_enemy(self) -> Optional[int]:
        """En yakın görünür düşmanı bul."""
        min_dist = float('inf')
        nearest_idx = None

        for i, (enemy, alive) in enumerate(zip(self._enemies, self._enemies_alive)):
            if not alive:
                continue

            dist = np.linalg.norm(enemy["position"] - self._bot_position)

            # Görünürlük kontrolü (basit)
            if dist < 0.8:  # Görüş mesafesi
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = i

        return nearest_idx

    def _get_observation(self) -> np.ndarray:
        """64-dim observation vector oluştur."""
        self._obs_builder.self_state = BotSelfState(
            health=self._bot_health,
            armor=0.5,
            ammo_primary=self._bot_ammo,
            ammo_secondary=0.5,
            pos_x=self._bot_position[0],
            pos_y=self._bot_position[1],
            pos_z=0.5,
            rotation_yaw=0.0,
            rotation_pitch=0.0,
            velocity_x=0.0,
            velocity_y=0.0,
            velocity_z=0.0,
            is_in_cover=float(self._bot_in_cover),
            is_reloading=0.0,
            is_aiming=0.0,
            time_since_damage=0.5
        )

        # Enemy observations
        for i in range(3):
            if i < len(self._enemies) and self._enemies_alive[i]:
                enemy = self._enemies[i]
                dist = np.linalg.norm(enemy["position"] - self._bot_position)
                angle = np.arctan2(
                    enemy["position"][1] - self._bot_position[1],
                    enemy["position"][0] - self._bot_position[0]
                ) / np.pi

                self._obs_builder.enemies[i] = EnemyState(
                    distance=min(dist, 1.0),
                    angle=angle,
                    health_estimate=enemy["health"],
                    is_visible=1.0 if dist < 0.8 else 0.0,
                    is_in_cover=float(enemy["in_cover"]),
                    threat_level=self.difficulty if enemy["aggressive"] else 0.3,
                    velocity_towards_me=0.0,
                    is_aiming_at_me=float(enemy["aggressive"])
                )
            else:
                self._obs_builder.enemies[i] = EnemyState()

        return self._obs_builder.build()

    def _get_info(self) -> Dict[str, Any]:
        """Ek bilgiler."""
        return {
            "step": self._step_count,
            "bot_health": self._bot_health,
            "bot_ammo": self._bot_ammo,
            "bot_kills": self._bot_kills,
            "enemies_alive": sum(self._enemies_alive),
            "damage_dealt": self._damage_dealt,
            "damage_taken": self._damage_taken,
            "total_reward": self._total_reward
        }

    def render(self) -> Optional[np.ndarray]:
        """Render (şimdilik sadece text)."""
        if self.render_mode == "human":
            print(f"\n=== Step {self._step_count} ===")
            print(f"Bot: HP={self._bot_health:.2f}, Ammo={self._bot_ammo:.2f}, "
                  f"Pos=({self._bot_position[0]:.2f}, {self._bot_position[1]:.2f}), "
                  f"Cover={self._bot_in_cover}")
            print(f"Kills: {self._bot_kills}, Enemies Alive: {sum(self._enemies_alive)}")
            print(f"Damage: Dealt={self._damage_dealt:.2f}, Taken={self._damage_taken:.2f}")

        return None

    def close(self) -> None:
        """Cleanup."""
        pass


# Gymnasium registration için
def make_mock_env(**kwargs):
    """Environment factory."""
    return MockCombatEnv(**kwargs)
