"""
Observation Space Definitions
TÜBİTAK İP-2 AI Bot System

64-boyutlu observation vector yapısı
"""

from dataclasses import dataclass, field
from typing import List, Dict
import numpy as np


@dataclass
class BotSelfState:
    """Bot'un kendi durumu (16 değer)"""
    health: float = 1.0               # 0-1 normalized
    armor: float = 1.0                # 0-1 normalized
    ammo_primary: float = 1.0         # 0-1 normalized
    ammo_secondary: float = 1.0       # 0-1 normalized
    pos_x: float = 0.5                # 0-1 normalized map position
    pos_y: float = 0.5
    pos_z: float = 0.5
    rotation_yaw: float = 0.0         # -1 to 1
    rotation_pitch: float = 0.0       # -1 to 1
    velocity_x: float = 0.0           # -1 to 1
    velocity_y: float = 0.0
    velocity_z: float = 0.0
    is_in_cover: float = 0.0          # 0 or 1
    is_reloading: float = 0.0         # 0 or 1
    is_aiming: float = 0.0            # 0 or 1
    time_since_damage: float = 1.0    # 0-1 normalized

    def to_array(self) -> np.ndarray:
        return np.array([
            self.health, self.armor, self.ammo_primary, self.ammo_secondary,
            self.pos_x, self.pos_y, self.pos_z,
            self.rotation_yaw, self.rotation_pitch,
            self.velocity_x, self.velocity_y, self.velocity_z,
            self.is_in_cover, self.is_reloading, self.is_aiming,
            self.time_since_damage
        ], dtype=np.float32)


@dataclass
class EnemyState:
    """Düşman durumu (8 değer per enemy)"""
    distance: float = 1.0             # 0-1 (0=yakın, 1=uzak)
    angle: float = 0.0                # -1 to 1 relative angle
    health_estimate: float = 1.0      # 0-1
    is_visible: float = 0.0           # 0 or 1
    is_in_cover: float = 0.0          # 0 or 1
    threat_level: float = 0.0         # 0-1
    velocity_towards_me: float = 0.0  # -1 to 1
    is_aiming_at_me: float = 0.0      # 0 or 1

    def to_array(self) -> np.ndarray:
        return np.array([
            self.distance, self.angle, self.health_estimate, self.is_visible,
            self.is_in_cover, self.threat_level, self.velocity_towards_me,
            self.is_aiming_at_me
        ], dtype=np.float32)


@dataclass
class EnvironmentState:
    """Çevre durumu (16 değer)"""
    # En yakın 4 siper (mesafe + açı)
    cover1_distance: float = 1.0
    cover1_angle: float = 0.0
    cover2_distance: float = 1.0
    cover2_angle: float = 0.0
    cover3_distance: float = 1.0
    cover3_angle: float = 0.0
    cover4_distance: float = 1.0
    cover4_angle: float = 0.0
    # Objective
    objective_distance: float = 1.0
    objective_angle: float = 0.0
    objective_progress: float = 0.0
    # Danger zone
    danger_zone_distance: float = 1.0
    danger_zone_angle: float = 0.0
    # General
    time_in_combat: float = 0.0
    enemies_in_range: float = 0.0
    allies_in_range: float = 0.0

    def to_array(self) -> np.ndarray:
        return np.array([
            self.cover1_distance, self.cover1_angle,
            self.cover2_distance, self.cover2_angle,
            self.cover3_distance, self.cover3_angle,
            self.cover4_distance, self.cover4_angle,
            self.objective_distance, self.objective_angle, self.objective_progress,
            self.danger_zone_distance, self.danger_zone_angle,
            self.time_in_combat, self.enemies_in_range, self.allies_in_range
        ], dtype=np.float32)


@dataclass
class TeamState:
    """Takım durumu (8 değer)"""
    team_health_avg: float = 1.0
    team_alive_ratio: float = 1.0
    nearest_ally_distance: float = 1.0
    nearest_ally_angle: float = 0.0
    team_objective_progress: float = 0.0
    team_kills: float = 0.0
    team_deaths: float = 0.0
    support_needed: float = 0.0

    def to_array(self) -> np.ndarray:
        return np.array([
            self.team_health_avg, self.team_alive_ratio,
            self.nearest_ally_distance, self.nearest_ally_angle,
            self.team_objective_progress, self.team_kills,
            self.team_deaths, self.support_needed
        ], dtype=np.float32)


class ObservationBuilder:
    """
    64-dim observation vector oluşturucu.

    Yapı:
    - [0-15]: Bot self state (16)
    - [16-39]: 3 enemy states (3 x 8 = 24)
    - [40-55]: Environment state (16)
    - [56-63]: Team state (8)
    Total: 64
    """

    OBSERVATION_DIM = 64
    MAX_ENEMIES = 3

    def __init__(self):
        self.self_state = BotSelfState()
        self.enemies: List[EnemyState] = [EnemyState() for _ in range(self.MAX_ENEMIES)]
        self.environment = EnvironmentState()
        self.team_state = TeamState()

    def build(self) -> np.ndarray:
        """64-dim observation vector oluştur."""
        obs = np.zeros(self.OBSERVATION_DIM, dtype=np.float32)

        # Self state [0-15]
        obs[0:16] = self.self_state.to_array()

        # Enemy states [16-39]
        for i, enemy in enumerate(self.enemies[:self.MAX_ENEMIES]):
            start_idx = 16 + i * 8
            obs[start_idx:start_idx + 8] = enemy.to_array()

        # Environment state [40-55]
        obs[40:56] = self.environment.to_array()

        # Team state [56-63]
        obs[56:64] = self.team_state.to_array()

        return obs

    def from_array(self, obs: np.ndarray) -> None:
        """Array'den state'leri parse et."""
        if len(obs) != self.OBSERVATION_DIM:
            raise ValueError(f"Expected {self.OBSERVATION_DIM} dims, got {len(obs)}")

        # Self state
        self.self_state = BotSelfState(
            health=obs[0], armor=obs[1],
            ammo_primary=obs[2], ammo_secondary=obs[3],
            pos_x=obs[4], pos_y=obs[5], pos_z=obs[6],
            rotation_yaw=obs[7], rotation_pitch=obs[8],
            velocity_x=obs[9], velocity_y=obs[10], velocity_z=obs[11],
            is_in_cover=obs[12], is_reloading=obs[13], is_aiming=obs[14],
            time_since_damage=obs[15]
        )

        # Enemies
        for i in range(self.MAX_ENEMIES):
            start = 16 + i * 8
            self.enemies[i] = EnemyState(
                distance=obs[start], angle=obs[start + 1],
                health_estimate=obs[start + 2], is_visible=obs[start + 3],
                is_in_cover=obs[start + 4], threat_level=obs[start + 5],
                velocity_towards_me=obs[start + 6], is_aiming_at_me=obs[start + 7]
            )

        # Environment [40-55]
        self.environment = EnvironmentState(
            cover1_distance=obs[40], cover1_angle=obs[41],
            cover2_distance=obs[42], cover2_angle=obs[43],
            cover3_distance=obs[44], cover3_angle=obs[45],
            cover4_distance=obs[46], cover4_angle=obs[47],
            objective_distance=obs[48], objective_angle=obs[49],
            objective_progress=obs[50],
            danger_zone_distance=obs[51], danger_zone_angle=obs[52],
            time_in_combat=obs[53], enemies_in_range=obs[54],
            allies_in_range=obs[55]
        )

        # Team [56-63]
        self.team_state = TeamState(
            team_health_avg=obs[56], team_alive_ratio=obs[57],
            nearest_ally_distance=obs[58], nearest_ally_angle=obs[59],
            team_objective_progress=obs[60], team_kills=obs[61],
            team_deaths=obs[62], support_needed=obs[63]
        )

    def get_description(self) -> Dict[str, str]:
        """Observation vector açıklaması."""
        return {
            "0-15": "Bot Self State (health, armor, ammo, position, velocity, flags)",
            "16-23": "Enemy 1 State (distance, angle, health, visible, cover, threat, velocity, aiming)",
            "24-31": "Enemy 2 State",
            "32-39": "Enemy 3 State",
            "40-55": "Environment State (covers, objective, danger zone, combat info)",
            "56-63": "Team State (health, alive ratio, ally info, objectives)"
        }
