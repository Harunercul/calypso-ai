"""
CALYPSO Observation Space Definitions
TÜBİTAK İP-2 AI Bot System

CALYPSO oyununa özel genişletilmiş observation space.
Tier bazlı düşman sistemi, kalkan mekaniği, alarm seviyeleri.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import IntEnum
import numpy as np


class EnemyTier(IntEnum):
    """CALYPSO Düşman Tier'leri"""
    TIER_1 = 1          # Düşük Güvenlik (Kolay)
    TIER_2 = 2          # Orta Seviye
    TIER_2_MARKSMAN = 3 # Nişancı
    TIER_2_ROBOTIC = 4  # Örümcek Mayın
    TIER_2_SPECIAL = 5  # Kalkanlı Birimler
    TIER_5_BOSS = 6     # Juggernaut


class WeaponType(IntEnum):
    """CALYPSO Silah Tipleri"""
    NONE = 0
    HG_PISTOL = 1      # Tabanca (Tier 1)
    SMG = 2            # Hafif Makinalı (Tier 1)
    AR_BURST = 3       # Burst Rifle (Tier 2)
    SG_SHOTGUN = 4     # Pompalı (Tier 2)
    DMR = 5            # Nişancı Tüfeği
    ENERGY_PISTOL = 6  # Enerji Tabancası (Kalkanlı)
    KINETIC_HAMMER = 7 # Kinetik Çekiç (Boss)


class AreaType(IntEnum):
    """Alan Tipleri"""
    NARROW = 0   # Dar (koridorlar)
    MEDIUM = 1   # Orta (odalar)
    WIDE = 2     # Geniş (salon, güverte)


class AlarmLevel(IntEnum):
    """Alarm Seviyeleri"""
    NONE = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3


@dataclass
class CalypsoBotState:
    """
    CALYPSO Bot Self State (20 değer)

    Standart 16 + 4 CALYPSO-özel değer
    """
    # Standart değerler (16)
    health: float = 1.0
    armor: float = 1.0
    ammo_primary: float = 1.0
    ammo_secondary: float = 0.0
    pos_x: float = 0.5
    pos_y: float = 0.5
    pos_z: float = 0.5
    rotation_yaw: float = 0.0
    rotation_pitch: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    velocity_z: float = 0.0
    is_in_cover: float = 0.0
    is_reloading: float = 0.0
    is_aiming: float = 0.0
    time_since_damage: float = 1.0

    # CALYPSO-özel (4)
    current_tier: float = 0.0      # 0-1 normalized (tier / 6)
    alarm_level: float = 0.0       # 0-1 normalized (alarm / 3)
    area_type: float = 0.0         # 0-1 normalized (area / 2)
    combat_phase: float = 0.0      # 0=gizlilik, 0.5=alarm, 1=aktif çatışma

    def to_array(self) -> np.ndarray:
        return np.array([
            self.health, self.armor, self.ammo_primary, self.ammo_secondary,
            self.pos_x, self.pos_y, self.pos_z,
            self.rotation_yaw, self.rotation_pitch,
            self.velocity_x, self.velocity_y, self.velocity_z,
            self.is_in_cover, self.is_reloading, self.is_aiming,
            self.time_since_damage,
            self.current_tier, self.alarm_level, self.area_type, self.combat_phase
        ], dtype=np.float32)


@dataclass
class CalypsoEnemyState:
    """
    CALYPSO Düşman Durumu (12 değer per enemy)

    Standart 8 + 4 CALYPSO-özel
    """
    # Standart (8)
    distance: float = 1.0
    angle: float = 0.0
    health_estimate: float = 1.0
    is_visible: float = 0.0
    is_in_cover: float = 0.0
    threat_level: float = 0.0
    velocity_towards_me: float = 0.0
    is_aiming_at_me: float = 0.0

    # CALYPSO-özel (4)
    tier: float = 0.0              # 0-1 normalized
    has_shield: float = 0.0        # 0 or 1
    shield_hp: float = 0.0         # 0-1 normalized
    weapon_type: float = 0.0       # 0-1 normalized (weapon / 7)

    def to_array(self) -> np.ndarray:
        return np.array([
            self.distance, self.angle, self.health_estimate, self.is_visible,
            self.is_in_cover, self.threat_level, self.velocity_towards_me,
            self.is_aiming_at_me,
            self.tier, self.has_shield, self.shield_hp, self.weapon_type
        ], dtype=np.float32)


@dataclass
class CalypsoEnvironmentState:
    """
    CALYPSO Çevre Durumu (20 değer)

    Standart 16 + 4 CALYPSO-özel
    """
    # Siper bilgileri (8)
    cover1_distance: float = 1.0
    cover1_angle: float = 0.0
    cover2_distance: float = 1.0
    cover2_angle: float = 0.0
    cover3_distance: float = 1.0
    cover3_angle: float = 0.0
    cover4_distance: float = 1.0
    cover4_angle: float = 0.0

    # Objective (3)
    objective_distance: float = 1.0
    objective_angle: float = 0.0
    objective_progress: float = 0.0

    # Tehlike (2)
    danger_zone_distance: float = 1.0
    danger_zone_angle: float = 0.0

    # Genel (3)
    time_in_combat: float = 0.0
    enemies_in_range: float = 0.0
    allies_in_range: float = 0.0

    # CALYPSO-özel (4)
    spider_mine_nearby: float = 0.0      # 0-1 (0=yok, 1=çok yakın)
    boss_phase: float = 0.0              # 0=yok, 0.33=idle, 0.66=attack, 1=defense
    shield_enemies_count: float = 0.0    # 0-1 normalized
    flank_route_available: float = 0.0   # 0 or 1

    def to_array(self) -> np.ndarray:
        return np.array([
            self.cover1_distance, self.cover1_angle,
            self.cover2_distance, self.cover2_angle,
            self.cover3_distance, self.cover3_angle,
            self.cover4_distance, self.cover4_angle,
            self.objective_distance, self.objective_angle, self.objective_progress,
            self.danger_zone_distance, self.danger_zone_angle,
            self.time_in_combat, self.enemies_in_range, self.allies_in_range,
            self.spider_mine_nearby, self.boss_phase,
            self.shield_enemies_count, self.flank_route_available
        ], dtype=np.float32)


@dataclass
class CalypsoTeamState:
    """
    CALYPSO Takım Durumu (8 değer)
    """
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


class CalypsoObservationBuilder:
    """
    CALYPSO 96-dim Observation Vector Builder

    Yapı:
    - [0-19]:  Bot self state (20)
    - [20-55]: 3 enemy states (3 x 12 = 36)
    - [56-75]: Environment state (20)
    - [76-83]: Team state (8)
    - [84-95]: CALYPSO tactical info (12)
    Total: 96
    """

    OBSERVATION_DIM = 96
    MAX_ENEMIES = 3

    def __init__(self):
        self.self_state = CalypsoBotState()
        self.enemies: List[CalypsoEnemyState] = [
            CalypsoEnemyState() for _ in range(self.MAX_ENEMIES)
        ]
        self.environment = CalypsoEnvironmentState()
        self.team_state = CalypsoTeamState()

        # Tactical info (12 değer)
        self.tactical_info = {
            'suppression_threat': 0.0,      # AR'lardan baskılama tehdidi
            'flank_threat': 0.0,            # SG'lerden kuşatma tehdidi
            'sniper_threat': 0.0,           # Keskin nişancı tehdidi
            'explosive_threat': 0.0,        # Bomba/spider mine tehdidi
            'shield_wall_active': 0.0,      # Kalkan duvarı var mı
            'retreat_path_clear': 0.0,      # Geri çekilme yolu açık mı
            'group_coordination': 0.0,      # Düşman grup koordinasyonu (0-1)
            'time_since_alarm': 0.0,        # Alarm başlangıcından geçen süre
            'reinforcement_eta': 0.0,       # Takviye gelme süresi
            'enemy_reload_window': 0.0,     # Düşman reload penceresi
            'boss_stun_window': 0.0,        # Boss sersemletme penceresi
            'player_skill_estimate': 0.5,   # Oyuncu yeteneği tahmini
        }

    def build(self) -> np.ndarray:
        """96-dim observation vector oluştur."""
        obs = np.zeros(self.OBSERVATION_DIM, dtype=np.float32)

        # Self state [0-19]
        obs[0:20] = self.self_state.to_array()

        # Enemy states [20-55]
        for i, enemy in enumerate(self.enemies[:self.MAX_ENEMIES]):
            start_idx = 20 + i * 12
            obs[start_idx:start_idx + 12] = enemy.to_array()

        # Environment state [56-75]
        obs[56:76] = self.environment.to_array()

        # Team state [76-83]
        obs[76:84] = self.team_state.to_array()

        # Tactical info [84-95]
        tactical_values = list(self.tactical_info.values())
        obs[84:96] = np.array(tactical_values, dtype=np.float32)

        # Clip to valid range [-1, 1]
        return np.clip(obs, -1.0, 1.0)

    def get_description(self) -> Dict[str, str]:
        """Observation vector açıklaması."""
        return {
            "0-19": "Bot Self State (health, armor, ammo, position, velocity, flags, tier, alarm, area)",
            "20-31": "Enemy 1 State (distance, angle, health, visible, cover, threat, velocity, aiming, tier, shield)",
            "32-43": "Enemy 2 State",
            "44-55": "Enemy 3 State",
            "56-75": "Environment State (covers, objective, danger, spider mine, boss phase)",
            "76-83": "Team State (health, alive ratio, ally info, objectives)",
            "84-95": "Tactical Info (threats, coordination, windows)"
        }


# =============================================================================
# CALYPSO Silah İstatistikleri
# =============================================================================

CALYPSO_WEAPONS = {
    WeaponType.HG_PISTOL: {
        'damage': 4,
        'rpm': 30,
        'magazine': 7,
        'reload_time': 2.0,
        'accuracy': 0.15,
        'range': 'short'
    },
    WeaponType.SMG: {
        'damage': 2,
        'rpm': 80,
        'magazine': 15,
        'reload_time': 3.0,
        'accuracy': 0.15,
        'range': 'short'
    },
    WeaponType.AR_BURST: {
        'damage': 6,  # x3 burst = 18
        'rpm': 50,
        'magazine': 30,
        'reload_time': 4.0,
        'accuracy': 0.40,
        'range': 'medium',
        'burst_count': 3,
        'burst_interval': 1.2
    },
    WeaponType.SG_SHOTGUN: {
        'damage': 15,
        'rpm': 30,
        'magazine': 8,
        'reload_time': 8.0,
        'accuracy': 0.40,
        'range': 'short',
        'fire_interval': 2.0
    },
    WeaponType.DMR: {
        'damage': 15,
        'rpm': 10,
        'magazine': 4,
        'reload_time': 10.0,
        'accuracy': 0.70,
        'range': 'long'
    },
    WeaponType.ENERGY_PISTOL: {
        'damage': 3,
        'rpm': 40,
        'magazine': 20,
        'reload_time': 3.0,
        'accuracy': 0.30,
        'range': 'medium'
    },
    WeaponType.KINETIC_HAMMER: {
        'damage': 100,
        'rpm': 20,
        'magazine': 999,
        'reload_time': 0,
        'accuracy': 0.90,
        'range': 'melee'
    }
}


# =============================================================================
# CALYPSO Tier İstatistikleri
# =============================================================================

CALYPSO_TIERS = {
    EnemyTier.TIER_1: {
        'health': 100,
        'armor': 0.10,
        'accuracy': 0.15,
        'speed': 1.1,  # medium_fast
        'weapons': [WeaponType.HG_PISTOL, WeaponType.SMG],
        'weapon_weights': [0.70, 0.30],
        'can_heal': False,
        'can_call_reinforcement': False,
        'behavior': 'panic'
    },
    EnemyTier.TIER_2: {
        'health': 150,
        'armor': 0.25,
        'accuracy': 0.40,
        'speed': 1.0,  # medium
        'weapons': [WeaponType.AR_BURST, WeaponType.SG_SHOTGUN],
        'weapon_weights': [0.60, 0.40],
        'can_heal': False,
        'can_call_reinforcement': True,
        'behavior': 'tactical'
    },
    EnemyTier.TIER_2_MARKSMAN: {
        'health': 50,
        'armor': 0.0,
        'accuracy': 0.70,
        'speed': 0.8,
        'weapons': [WeaponType.DMR],
        'weapon_weights': [1.0],
        'can_heal': False,
        'can_call_reinforcement': False,
        'behavior': 'sniper'
    },
    EnemyTier.TIER_2_ROBOTIC: {
        'body_health': 250,
        'leg_health': 50,
        'leg_count': 4,
        'armor': 0.0,
        'speed': 0.9,
        'explosion_damage': 0.60,  # %60 player HP
        'behavior': 'spider_mine'
    },
    EnemyTier.TIER_2_SPECIAL: {
        'health': 150,
        'armor': 0.25,
        'shield_hp': 500,  # Plasma: 500 (regenerates), Iron-Clad: 2000 (no regen)
        'shield_regen': 6.0,  # seconds
        'accuracy': 0.35,
        'speed': 1.0,
        'weapons': [WeaponType.ENERGY_PISTOL],
        'weapon_weights': [1.0],
        'behavior': 'shielded'
    },
    EnemyTier.TIER_5_BOSS: {
        'health': 1000,
        'armor': 0.50,
        'armor_defense_mode': 0.90,
        'accuracy': 0.90,
        'speed': 0.8,
        'speed_defense': 0.5,
        'weapons': [WeaponType.KINETIC_HAMMER],
        'weapon_weights': [1.0],
        'behavior': 'boss_pattern'
    }
}
