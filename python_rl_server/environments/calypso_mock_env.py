"""
CALYPSO Mock Combat Environment
TÜBİTAK İP-2 AI Bot System

CALYPSO oyununa özel mock environment.
Tier bazlı düşman sistemi, alarm mekanikleri, kalkan mekaniği.
"""

from typing import Any, Dict, Optional, Tuple, List
from enum import IntEnum
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from .calypso_observation import (
    CalypsoObservationBuilder, CalypsoBotState, CalypsoEnemyState,
    CalypsoEnvironmentState, CalypsoTeamState,
    EnemyTier, WeaponType, AreaType, AlarmLevel,
    CALYPSO_WEAPONS, CALYPSO_TIERS
)


class CalypsoAction(IntEnum):
    """CALYPSO 16 Aksiyon"""
    # Temel (0-4)
    IDLE = 0
    ATTACK = 1
    TAKE_COVER = 2
    FLEE = 3
    RELOAD = 4

    # Hareket (5-7)
    PATROL = 5
    INVESTIGATE = 6
    ADVANCE = 7

    # Taktik (8-11)
    FLANK = 8
    SUPPORT = 9
    SUPPRESS = 10
    PEEK_FIRE = 11

    # CALYPSO Özel (12-15)
    TARGET_WEAK_POINT = 12    # Zayıf noktayı hedefle (kalkan battery, boss LED)
    EVADE_EXPLOSIVE = 13      # Patlayıcıdan kaçın (spider mine, grenade)
    COUNTER_SHIELD = 14       # Kalkan karşı manevrası
    COORDINATE_ATTACK = 15    # Koordineli saldırı (grup taktiği)


class CalypsoMockEnv(gym.Env):
    """
    CALYPSO Mock Combat Environment

    Tier bazlı düşman sistemi ile TPS savaş simülasyonu.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(
        self,
        render_mode: Optional[str] = None,
        max_steps: int = 2000,
        initial_tier: int = 1,
        alarm_level: int = 1,
        area_type: int = 1,
        enable_boss: bool = False,
        player_skill: float = 0.5
    ):
        """
        Args:
            render_mode: "human" veya "rgb_array"
            max_steps: Episode başına maksimum step
            initial_tier: Başlangıç düşman tier'i (1, 2, 5)
            alarm_level: Alarm seviyesi (1, 2, 3)
            area_type: Alan tipi (0=narrow, 1=medium, 2=wide)
            enable_boss: Boss spawn aktif mi
            player_skill: Oyuncu yeteneği tahmini (0-1)
        """
        super().__init__()

        self.render_mode = render_mode
        self.max_steps = max_steps
        self.initial_tier = initial_tier
        self.alarm_level = alarm_level
        self.area_type = AreaType(area_type)
        self.enable_boss = enable_boss
        self.player_skill = player_skill

        # 96-dim observation, 16 discrete actions
        # Observation range: -1 to 1 (angles can be negative)
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(96,),
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(16)

        # State
        self._obs_builder = CalypsoObservationBuilder()
        self._step_count = 0
        self._total_reward = 0.0
        self._time_since_alarm = 0.0

        # Bot state
        self._bot_health = 1.0
        self._bot_armor = 0.0
        self._bot_ammo = 1.0
        self._bot_position = np.array([0.5, 0.5])
        self._bot_in_cover = False
        self._bot_kills = 0

        # Enemy management
        self._enemies: List[Dict] = []
        self._spider_mines: List[Dict] = []
        self._boss: Optional[Dict] = None

        # Combat stats
        self._damage_dealt = 0.0
        self._damage_taken = 0.0

        # Spawn timers
        self._spawn_timer = 0.0
        self._marksman_timer = 0.0
        self._spider_timer = 0.0
        self._reinforcement_timer = 0.0

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict]:
        """Environment'ı sıfırla."""
        super().reset(seed=seed)

        self._step_count = 0
        self._total_reward = 0.0
        self._time_since_alarm = 0.0

        # Bot reset
        self._bot_health = 1.0
        self._bot_armor = 0.0
        self._bot_ammo = 1.0
        self._bot_position = np.array([0.5, 0.5])
        self._bot_in_cover = False
        self._bot_kills = 0
        self._damage_dealt = 0.0
        self._damage_taken = 0.0

        # Spawn timers
        self._spawn_timer = 0.0
        self._marksman_timer = 0.0
        self._spider_timer = 0.0
        self._reinforcement_timer = 0.0

        # Initial enemy spawn based on tier
        self._enemies = []
        self._spider_mines = []
        self._boss = None

        self._spawn_initial_enemies()

        obs = self._get_observation()
        info = self._get_info()

        return obs, info

    def _spawn_initial_enemies(self) -> None:
        """Başlangıç düşmanlarını spawn et."""
        if self.initial_tier == 1:
            # Tier 1: 3-5 kişi
            count = self.np_random.integers(3, 6)
            for _ in range(count):
                self._spawn_tier1_enemy()

        elif self.initial_tier == 2:
            # Tier 2: 9 kişilik karma grup (dokümana göre)
            # 2 Kalkan + 4 AR + 3 SG
            for _ in range(2):
                self._spawn_tier2_special_enemy('plasma_shield')
            for _ in range(4):
                self._spawn_tier2_enemy('ar')
            for _ in range(3):
                self._spawn_tier2_enemy('sg')

        if self.enable_boss:
            self._spawn_boss()

    def _spawn_tier1_enemy(self) -> None:
        """Tier 1 düşman spawn et."""
        tier_stats = CALYPSO_TIERS[EnemyTier.TIER_1]

        # Silah seçimi (%70 HG, %30 SMG)
        weapon = self.np_random.choice(
            tier_stats['weapons'],
            p=tier_stats['weapon_weights']
        )

        enemy = {
            'tier': EnemyTier.TIER_1,
            'health': tier_stats['health'] / 100.0,  # normalized
            'max_health': tier_stats['health'],
            'armor': tier_stats['armor'],
            'accuracy': tier_stats['accuracy'],
            'weapon': weapon,
            'position': np.array([
                self.np_random.uniform(0.2, 0.8),
                self.np_random.uniform(0.2, 0.8)
            ]),
            'in_cover': False,
            'alive': True,
            'state': 'patrol',  # patrol, surprised, panic_fire, fleeing, passive
            'state_timer': 0.0,
            'ammo': CALYPSO_WEAPONS[weapon]['magazine'],
            'has_shield': False,
            'shield_hp': 0.0
        }
        self._enemies.append(enemy)

    def _spawn_tier2_enemy(self, variant: str = 'ar') -> None:
        """Tier 2 düşman spawn et."""
        tier_stats = CALYPSO_TIERS[EnemyTier.TIER_2]

        weapon = WeaponType.AR_BURST if variant == 'ar' else WeaponType.SG_SHOTGUN
        role = 'suppression' if variant == 'ar' else 'flanker'

        enemy = {
            'tier': EnemyTier.TIER_2,
            'health': tier_stats['health'] / 150.0,
            'max_health': tier_stats['health'],
            'armor': tier_stats['armor'],
            'accuracy': tier_stats['accuracy'],
            'weapon': weapon,
            'role': role,
            'position': np.array([
                self.np_random.uniform(0.2, 0.8),
                self.np_random.uniform(0.2, 0.8)
            ]),
            'in_cover': self.np_random.random() < 0.5,
            'alive': True,
            'state': 'tactical',  # tactical, suppressing, flanking, retreating
            'state_timer': 0.0,
            'ammo': CALYPSO_WEAPONS[weapon]['magazine'],
            'has_grenade': self.np_random.random() < 0.40,  # %40 şans
            'grenade_cooldown': 0.0,
            'has_shield': False,
            'shield_hp': 0.0
        }
        self._enemies.append(enemy)

    def _spawn_tier2_special_enemy(self, variant: str = 'plasma_shield') -> None:
        """Tier 2 Special düşman spawn et."""
        tier_stats = CALYPSO_TIERS[EnemyTier.TIER_2_SPECIAL]

        if variant == 'plasma_shield':
            shield_hp = 500
            shield_regen = True
        else:  # iron_clad
            shield_hp = 2000
            shield_regen = False

        enemy = {
            'tier': EnemyTier.TIER_2_SPECIAL,
            'health': tier_stats['health'] / 150.0,
            'max_health': tier_stats['health'],
            'armor': tier_stats['armor'],
            'accuracy': tier_stats.get('accuracy', 0.35),
            'weapon': WeaponType.ENERGY_PISTOL,
            'position': np.array([
                self.np_random.uniform(0.3, 0.7),
                self.np_random.uniform(0.3, 0.7)
            ]),
            'in_cover': False,
            'alive': True,
            'state': 'advancing',
            'state_timer': 0.0,
            'has_shield': True,
            'shield_hp': shield_hp / shield_hp,  # normalized
            'max_shield_hp': shield_hp,
            'shield_regen': shield_regen,
            'shield_regen_timer': 0.0,
            'weak_point_location': self.np_random.choice(['back', 'left_shoulder', 'right_shoulder', 'head']),
            'weak_point_hp': 125,
            'ammo': 20
        }
        self._enemies.append(enemy)

    def _spawn_spider_mine(self) -> None:
        """Örümcek mayın spawn et."""
        spider = {
            'body_health': 250 / 250,
            'leg_health': [50/50, 50/50, 50/50, 50/50],  # 4 bacak
            'position': np.array([
                self.np_random.uniform(0.1, 0.9),
                self.np_random.uniform(0.1, 0.9)
            ]),
            'alive': True,
            'exploding': False,
            'explosion_timer': 0.0,
            'state': 'approaching'  # approaching, wall_crawl, ceiling, exploding
        }
        self._spider_mines.append(spider)

    def _spawn_marksman(self) -> None:
        """Marksman spawn et."""
        tier_stats = CALYPSO_TIERS[EnemyTier.TIER_2_MARKSMAN]

        enemy = {
            'tier': EnemyTier.TIER_2_MARKSMAN,
            'health': tier_stats['health'] / 50.0,
            'max_health': tier_stats['health'],
            'armor': 0,
            'accuracy': tier_stats['accuracy'],
            'weapon': WeaponType.DMR,
            'position': np.array([
                self.np_random.uniform(0.7, 0.95),  # Uzak pozisyon
                self.np_random.uniform(0.1, 0.9)
            ]),
            'in_cover': True,
            'alive': True,
            'state': 'sniping',
            'state_timer': 0.0,
            'ammo': 4,
            'has_shield': False,
            'shield_hp': 0.0
        }
        self._enemies.append(enemy)

    def _spawn_boss(self) -> None:
        """Juggernaut boss spawn et."""
        tier_stats = CALYPSO_TIERS[EnemyTier.TIER_5_BOSS]

        self._boss = {
            'health': tier_stats['health'] / 1000.0,
            'max_health': tier_stats['health'],
            'armor': tier_stats['armor'],
            'armor_current': tier_stats['armor'],
            'position': np.array([0.8, 0.5]),
            'alive': True,
            'state': 'walking',  # walking, hammer_combo, leap, defense, stunned
            'state_timer': 0.0,
            'stun_timer': 0.0,
            'is_stunned': False,
            'weak_points_visible': False,
            'attack_combo': 0
        }

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Bir step simüle et."""
        self._step_count += 1
        self._time_since_alarm += 0.033  # ~30fps
        reward = 0.0

        # Action'a göre işlem
        reward += self._execute_action(action)

        # Düşman aksiyonları
        self._enemy_actions()

        # Spawn yönetimi
        self._manage_spawns()

        # Survival bonus
        if self._bot_health > 0:
            reward += 0.01

        self._total_reward += reward

        # Terminal conditions
        terminated = False
        truncated = False

        if self._bot_health <= 0:
            terminated = True
            reward -= 10.0

        if self._all_enemies_dead() and (self._boss is None or not self._boss['alive']):
            terminated = True
            reward += 30.0

        if self._step_count >= self.max_steps:
            truncated = True

        obs = self._get_observation()
        info = self._get_info()

        return obs, reward, terminated, truncated, info

    def _execute_action(self, action: int) -> float:
        """Seçilen aksiyonu çalıştır."""
        action = CalypsoAction(action)

        if action == CalypsoAction.IDLE:
            return 0.01

        elif action == CalypsoAction.ATTACK:
            return self._do_attack()

        elif action == CalypsoAction.TAKE_COVER:
            return self._do_take_cover()

        elif action == CalypsoAction.FLEE:
            return self._do_flee()

        elif action == CalypsoAction.RELOAD:
            return self._do_reload()

        elif action == CalypsoAction.PATROL:
            return self._do_patrol()

        elif action == CalypsoAction.INVESTIGATE:
            return self._do_investigate()

        elif action == CalypsoAction.ADVANCE:
            return self._do_advance()

        elif action == CalypsoAction.FLANK:
            return self._do_flank()

        elif action == CalypsoAction.SUPPORT:
            return self._do_support()

        elif action == CalypsoAction.SUPPRESS:
            return self._do_suppress()

        elif action == CalypsoAction.PEEK_FIRE:
            return self._do_peek_fire()

        elif action == CalypsoAction.TARGET_WEAK_POINT:
            return self._do_target_weak_point()

        elif action == CalypsoAction.EVADE_EXPLOSIVE:
            return self._do_evade_explosive()

        elif action == CalypsoAction.COUNTER_SHIELD:
            return self._do_counter_shield()

        elif action == CalypsoAction.COORDINATE_ATTACK:
            return self._do_coordinate_attack()

        return 0.0

    def _do_attack(self) -> float:
        """Standart saldırı."""
        reward = 0.0

        if self._bot_ammo <= 0:
            return -0.1

        self._bot_ammo = max(0, self._bot_ammo - 0.1)

        target = self._find_best_target()
        if target is None:
            return -0.05

        hit = self._calculate_hit(target)
        if hit:
            damage = 0.15 * (1 if not target.get('has_shield') else 0.3)

            if target.get('has_shield') and target.get('shield_hp', 0) > 0:
                target['shield_hp'] = max(0, target['shield_hp'] - damage)
                reward += 0.5
            else:
                target['health'] = max(0, target['health'] - damage)
                self._damage_dealt += damage
                reward += 1.0

            if target['health'] <= 0:
                target['alive'] = False
                self._bot_kills += 1
                reward += self._get_kill_reward(target)

        return reward

    def _do_take_cover(self) -> float:
        """Sipere gir."""
        if self._bot_in_cover:
            return -0.01

        self._bot_in_cover = True
        return 0.5

    def _do_flee(self) -> float:
        """Kaç."""
        direction = self.np_random.uniform(-1, 1, 2)
        direction = direction / (np.linalg.norm(direction) + 1e-8)

        self._bot_position += direction * 0.15
        self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
        self._bot_in_cover = False

        if self._bot_health < 0.3:
            return 0.5
        return 0.0

    def _do_reload(self) -> float:
        """Mermi doldur."""
        if self._bot_ammo >= 1.0:
            return -0.05

        self._bot_ammo = min(1.0, self._bot_ammo + 0.5)

        if self._bot_in_cover:
            return 0.3
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
        """En yakın düşmana doğru hareket."""
        nearest = self._find_nearest_enemy()
        if nearest is None:
            return 0.0

        direction = nearest['position'] - self._bot_position
        direction = direction / (np.linalg.norm(direction) + 1e-8)

        self._bot_position += direction * 0.05
        self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
        self._bot_in_cover = False

        return 0.05

    def _do_advance(self) -> float:
        """Agresif ilerleme."""
        target = self._find_best_target()
        if target is None:
            return 0.0

        direction = target['position'] - self._bot_position
        direction = direction / (np.linalg.norm(direction) + 1e-8)

        self._bot_position += direction * 0.08
        self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
        self._bot_in_cover = False

        return 0.1

    def _do_flank(self) -> float:
        """Yan manevra."""
        target = self._find_best_target()
        if target is None:
            return 0.0

        direction = target['position'] - self._bot_position
        perpendicular = np.array([-direction[1], direction[0]])
        perpendicular = perpendicular / (np.linalg.norm(perpendicular) + 1e-8)

        self._bot_position += perpendicular * 0.12
        self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
        self._bot_in_cover = False

        return 0.4

    def _do_support(self) -> float:
        """Takım desteği."""
        self._bot_position += self.np_random.uniform(-0.05, 0.05, 2)
        self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
        return 0.15

    def _do_suppress(self) -> float:
        """Baskılama ateşi."""
        if self._bot_ammo <= 0.2:
            return -0.1

        self._bot_ammo = max(0, self._bot_ammo - 0.2)

        # Tüm görünür düşmanları sipere zorla
        reward = 0.0
        for enemy in self._enemies:
            if not enemy['alive']:
                continue
            dist = np.linalg.norm(enemy['position'] - self._bot_position)
            if dist < 0.7:
                if not enemy['in_cover']:
                    enemy['in_cover'] = True
                    reward += 0.3

        return reward

    def _do_peek_fire(self) -> float:
        """Siperden peek-fire."""
        if not self._bot_in_cover:
            return -0.1

        if self._bot_ammo <= 0:
            return -0.1

        self._bot_ammo = max(0, self._bot_ammo - 0.05)

        target = self._find_best_target()
        if target is None:
            return 0.0

        # Düşük hasar ama güvenli
        if self.np_random.random() < 0.4:
            damage = 0.08
            if target.get('has_shield') and target.get('shield_hp', 0) > 0:
                target['shield_hp'] = max(0, target['shield_hp'] - damage * 0.3)
            else:
                target['health'] = max(0, target['health'] - damage)
            return 0.6

        return 0.1

    def _do_target_weak_point(self) -> float:
        """Zayıf noktayı hedefle."""
        # Kalkanlı düşman veya boss
        target = None

        # Boss öncelikli
        if self._boss and self._boss['alive'] and self._boss['is_stunned']:
            target = self._boss
            if self.np_random.random() < 0.6:
                self._boss['health'] -= 0.1
                self._damage_dealt += 0.1
                if self._boss['health'] <= 0:
                    self._boss['alive'] = False
                    return 50.0  # Boss kill
                return 5.0
            return 0.5

        # Kalkanlı düşman
        for enemy in self._enemies:
            if enemy['alive'] and enemy.get('has_shield'):
                if self.np_random.random() < 0.4:
                    enemy['weak_point_hp'] = enemy.get('weak_point_hp', 125) - 30
                    if enemy['weak_point_hp'] <= 0:
                        enemy['has_shield'] = False
                        enemy['shield_hp'] = 0
                        return 3.0
                    return 1.0
                return 0.2

        return -0.1  # Hedef yok

    def _do_evade_explosive(self) -> float:
        """Patlayıcıdan kaçın."""
        # Spider mine kontrolü
        for spider in self._spider_mines:
            if spider['alive']:
                dist = np.linalg.norm(spider['position'] - self._bot_position)
                if dist < 0.3:
                    # Uzaklaş
                    direction = self._bot_position - spider['position']
                    direction = direction / (np.linalg.norm(direction) + 1e-8)
                    self._bot_position += direction * 0.2
                    self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
                    return 1.0

        return 0.0

    def _do_counter_shield(self) -> float:
        """Kalkan karşı manevrası."""
        # Kalkanlı düşmanın arkasına geç
        for enemy in self._enemies:
            if enemy['alive'] and enemy.get('has_shield'):
                direction = enemy['position'] - self._bot_position
                perpendicular = np.array([-direction[1], direction[0]])
                perpendicular = perpendicular / (np.linalg.norm(perpendicular) + 1e-8)

                self._bot_position += perpendicular * 0.15
                self._bot_position = np.clip(self._bot_position, 0.0, 1.0)
                self._bot_in_cover = False

                # Arkadan saldırı şansı
                if self.np_random.random() < 0.3:
                    enemy['weak_point_hp'] = enemy.get('weak_point_hp', 125) - 40
                    if enemy['weak_point_hp'] <= 0:
                        enemy['has_shield'] = False
                        return 4.0
                    return 1.5

                return 0.5

        return -0.1

    def _do_coordinate_attack(self) -> float:
        """Koordineli saldırı."""
        # Simüle edilmiş koordinasyon bonusu
        visible_enemies = sum(1 for e in self._enemies if e['alive'] and
                              np.linalg.norm(e['position'] - self._bot_position) < 0.6)

        if visible_enemies >= 2:
            # Grup saldırısı simülasyonu
            for enemy in self._enemies:
                if enemy['alive'] and np.linalg.norm(enemy['position'] - self._bot_position) < 0.6:
                    if self.np_random.random() < 0.25:
                        enemy['health'] -= 0.1
                        if enemy['health'] <= 0:
                            enemy['alive'] = False
                            self._bot_kills += 1
            return 0.8

        return 0.0

    def _enemy_actions(self) -> None:
        """Düşman aksiyonları."""
        # Tier bazlı davranışlar
        for enemy in self._enemies:
            if not enemy['alive']:
                continue

            if enemy['tier'] == EnemyTier.TIER_1:
                self._tier1_behavior(enemy)
            elif enemy['tier'] == EnemyTier.TIER_2:
                self._tier2_behavior(enemy)
            elif enemy['tier'] == EnemyTier.TIER_2_MARKSMAN:
                self._marksman_behavior(enemy)
            elif enemy['tier'] == EnemyTier.TIER_2_SPECIAL:
                self._shield_behavior(enemy)

        # Spider mine davranışları
        self._spider_mine_actions()

        # Boss davranışları
        if self._boss and self._boss['alive']:
            self._boss_behavior()

    def _tier1_behavior(self, enemy: Dict) -> None:
        """Tier 1 panik davranışı."""
        dist = np.linalg.norm(enemy['position'] - self._bot_position)
        enemy['state_timer'] += 0.033

        if enemy['state'] == 'patrol':
            # Oyuncuyu gördü mü?
            if dist < 0.6:
                enemy['state'] = 'surprised'
                enemy['state_timer'] = 0.0

        elif enemy['state'] == 'surprised':
            # 1.5s şaşkınlık
            if enemy['state_timer'] >= 1.5:
                enemy['state'] = 'panic_fire'
                enemy['state_timer'] = 0.0

        elif enemy['state'] == 'panic_fire':
            # 2s kontrolsüz ateş
            if enemy['state_timer'] < 2.0:
                if self.np_random.random() < enemy['accuracy'] * 0.5:  # Yarı isabet
                    if not self._bot_in_cover:
                        damage = 0.02
                        self._bot_health -= damage
                        self._damage_taken += damage
            else:
                enemy['state'] = 'fleeing'
                enemy['state_timer'] = 0.0

        elif enemy['state'] == 'fleeing':
            # Sipere kaç
            direction = self._bot_position - enemy['position']
            direction = -direction / (np.linalg.norm(direction) + 1e-8)
            enemy['position'] += direction * 0.08
            enemy['position'] = np.clip(enemy['position'], 0.0, 1.0)

            if enemy['state_timer'] >= 1.0:
                enemy['in_cover'] = True
                enemy['state'] = 'passive'
                enemy['state_timer'] = 0.0

        elif enemy['state'] == 'passive':
            # 7s bekleme
            enemy['in_cover'] = True
            if enemy['state_timer'] >= 7.0:
                enemy['state'] = 'panic_fire'
                enemy['state_timer'] = 0.0

    def _tier2_behavior(self, enemy: Dict) -> None:
        """Tier 2 taktiksel davranış."""
        dist = np.linalg.norm(enemy['position'] - self._bot_position)
        enemy['state_timer'] += 0.033

        role = enemy.get('role', 'suppression')

        if role == 'suppression':
            # AR baskılama
            if self._bot_in_cover and dist < 0.6:
                if self.np_random.random() < 0.3:
                    if self.np_random.random() < enemy['accuracy']:
                        damage = 0.03
                        self._bot_health -= damage * 0.3  # Cover azaltır
                        self._damage_taken += damage * 0.3
            else:
                # Normal ateş
                if self.np_random.random() < 0.2:
                    if self.np_random.random() < enemy['accuracy']:
                        if not self._bot_in_cover:
                            damage = 0.05
                            self._bot_health -= damage
                            self._damage_taken += damage

        elif role == 'flanker':
            # SG kuşatma
            if dist < 0.4 and not self._bot_in_cover:
                # Yakın mesafe shotgun
                if self.np_random.random() < 0.15:
                    damage = 0.12
                    self._bot_health -= damage
                    self._damage_taken += damage
            else:
                # Sprint ile yaklaş
                direction = self._bot_position - enemy['position']
                perpendicular = np.array([-direction[1], direction[0]])
                perpendicular = perpendicular / (np.linalg.norm(perpendicular) + 1e-8)

                enemy['position'] += perpendicular * 0.06
                enemy['position'] = np.clip(enemy['position'], 0.0, 1.0)

    def _marksman_behavior(self, enemy: Dict) -> None:
        """Marksman uzak mesafe davranışı."""
        dist = np.linalg.norm(enemy['position'] - self._bot_position)

        if dist > 0.5:  # Uzak mesafe
            if self.np_random.random() < 0.1:
                if self.np_random.random() < enemy['accuracy']:
                    if not self._bot_in_cover:
                        damage = 0.15
                        self._bot_health -= damage
                        self._damage_taken += damage
                    else:
                        damage = 0.05
                        self._bot_health -= damage
                        self._damage_taken += damage

    def _shield_behavior(self, enemy: Dict) -> None:
        """Kalkanlı birim davranışı."""
        dist = np.linalg.norm(enemy['position'] - self._bot_position)

        # Kalkan yenileme (Plasma)
        if enemy.get('shield_regen') and enemy.get('shield_hp', 0) <= 0:
            enemy['shield_regen_timer'] += 0.033
            if enemy['shield_regen_timer'] >= 6.0:
                enemy['shield_hp'] = 1.0
                enemy['shield_regen_timer'] = 0.0

        # İlerleme
        if dist > 0.3:
            direction = self._bot_position - enemy['position']
            direction = direction / (np.linalg.norm(direction) + 1e-8)
            enemy['position'] += direction * 0.03
            enemy['position'] = np.clip(enemy['position'], 0.0, 1.0)

        # Düşük hasarlı saldırı
        if dist < 0.5:
            if self.np_random.random() < 0.1:
                damage = 0.02
                if self._bot_in_cover:
                    damage *= 0.3
                self._bot_health -= damage
                self._damage_taken += damage

    def _spider_mine_actions(self) -> None:
        """Örümcek mayın davranışları."""
        for spider in self._spider_mines:
            if not spider['alive']:
                continue

            dist = np.linalg.norm(spider['position'] - self._bot_position)

            if spider['exploding']:
                spider['explosion_timer'] += 0.033
                if spider['explosion_timer'] >= 2.5:
                    # PATLAMA
                    if dist < 0.2:
                        self._bot_health -= 0.6
                        self._damage_taken += 0.6
                    spider['alive'] = False
            else:
                # Yaklaş
                if dist > 0.15:
                    direction = self._bot_position - spider['position']
                    direction = direction / (np.linalg.norm(direction) + 1e-8)
                    spider['position'] += direction * 0.04
                else:
                    # Patlamayı başlat
                    spider['exploding'] = True
                    spider['explosion_timer'] = 0.0

    def _boss_behavior(self) -> None:
        """Juggernaut boss davranışı."""
        boss = self._boss
        dist = np.linalg.norm(boss['position'] - self._bot_position)
        boss['state_timer'] += 0.033

        if boss['is_stunned']:
            boss['stun_timer'] += 0.033
            boss['weak_points_visible'] = True
            if boss['stun_timer'] >= 3.0:
                boss['is_stunned'] = False
                boss['weak_points_visible'] = False
                boss['state'] = 'walking'
                boss['state_timer'] = 0.0
            return

        if boss['state'] == 'walking':
            # Yavaş yaklaş
            direction = self._bot_position - boss['position']
            direction = direction / (np.linalg.norm(direction) + 1e-8)
            boss['position'] += direction * 0.02
            boss['position'] = np.clip(boss['position'], 0.0, 1.0)

            if dist < 0.25:
                boss['state'] = 'hammer_combo'
                boss['state_timer'] = 0.0
                boss['attack_combo'] = 0

        elif boss['state'] == 'hammer_combo':
            # 3 vuruşluk combo
            if boss['state_timer'] >= 0.8:
                boss['attack_combo'] += 1

                if boss['attack_combo'] <= 2:
                    # Zayıf vuruş
                    if dist < 0.2:
                        damage = 0.15
                        self._bot_health -= damage
                        self._damage_taken += damage
                else:
                    # Güçlü vuruş + stun
                    if dist < 0.25:
                        damage = 0.3
                        self._bot_health -= damage
                        self._damage_taken += damage

                boss['state_timer'] = 0.0

                if boss['attack_combo'] >= 3:
                    boss['state'] = 'walking'
                    boss['attack_combo'] = 0

        elif boss['state'] == 'leap':
            # Zıplama saldırısı
            if boss['state_timer'] < 0.5:
                direction = self._bot_position - boss['position']
                direction = direction / (np.linalg.norm(direction) + 1e-8)
                boss['position'] += direction * 0.15
                boss['position'] = np.clip(boss['position'], 0.0, 1.0)
            else:
                # İniş hasarı
                if dist < 0.3:
                    damage = 0.2
                    self._bot_health -= damage
                    self._damage_taken += damage

                # Duvara çarptı mı? (kenar kontrolü)
                if np.any(boss['position'] <= 0.05) or np.any(boss['position'] >= 0.95):
                    boss['is_stunned'] = True
                    boss['stun_timer'] = 0.0

                boss['state'] = 'walking'
                boss['state_timer'] = 0.0

        elif boss['state'] == 'defense':
            # Savunma modu - %90 hasar azaltma
            boss['armor_current'] = 0.90
            if boss['state_timer'] >= 5.0:
                boss['armor_current'] = 0.50
                boss['state'] = 'walking'

    def _manage_spawns(self) -> None:
        """Spawn yönetimi."""
        self._spawn_timer += 0.033
        self._marksman_timer += 0.033
        self._spider_timer += 0.033

        # Tier 1: Her 30s'de 3-5 kişi
        if self.initial_tier == 1 and self._spawn_timer >= 30.0:
            count = self.np_random.integers(3, 6)
            for _ in range(min(count, 5 - sum(1 for e in self._enemies if e['alive']))):
                self._spawn_tier1_enemy()
            self._spawn_timer = 0.0

        # Marksman: Her 90s'de 1-2 adet (tier 2 sonrası)
        if self.initial_tier >= 2 and self._marksman_timer >= 90.0:
            if self.area_type == AreaType.WIDE:
                for _ in range(self.np_random.integers(1, 3)):
                    self._spawn_marksman()
            self._marksman_timer = 0.0

        # Spider mine: 45s aralıklarla
        if self._time_since_alarm >= 45.0:
            if self._spider_timer >= 45.0:
                if len([s for s in self._spider_mines if s['alive']]) < 3:
                    self._spawn_spider_mine()
                self._spider_timer = 0.0

    def _find_best_target(self) -> Optional[Dict]:
        """En iyi hedefi bul."""
        best_target = None
        best_score = -999

        for enemy in self._enemies:
            if not enemy['alive']:
                continue

            dist = np.linalg.norm(enemy['position'] - self._bot_position)
            if dist > 0.8:
                continue

            score = 1.0 - dist
            if enemy.get('has_shield'):
                score -= 0.3
            if enemy['health'] < 0.3:
                score += 0.5
            if enemy['tier'] == EnemyTier.TIER_2_MARKSMAN:
                score += 0.4

            if score > best_score:
                best_score = score
                best_target = enemy

        return best_target

    def _find_nearest_enemy(self) -> Optional[Dict]:
        """En yakın düşmanı bul."""
        nearest = None
        min_dist = float('inf')

        for enemy in self._enemies:
            if not enemy['alive']:
                continue
            dist = np.linalg.norm(enemy['position'] - self._bot_position)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy

        return nearest

    def _calculate_hit(self, target: Dict) -> bool:
        """İsabet hesapla."""
        dist = np.linalg.norm(target['position'] - self._bot_position)
        hit_chance = max(0.2, 0.8 - dist * 0.5)

        if target.get('in_cover'):
            hit_chance *= 0.5
        if target.get('has_shield') and target.get('shield_hp', 0) > 0:
            hit_chance *= 0.7

        return self.np_random.random() < hit_chance

    def _get_kill_reward(self, enemy: Dict) -> float:
        """Kill reward tier'e göre."""
        tier = enemy.get('tier', EnemyTier.TIER_1)

        if tier == EnemyTier.TIER_1:
            return 5.0
        elif tier == EnemyTier.TIER_2:
            return 8.0
        elif tier == EnemyTier.TIER_2_MARKSMAN:
            return 10.0
        elif tier == EnemyTier.TIER_2_SPECIAL:
            return 15.0

        return 5.0

    def _all_enemies_dead(self) -> bool:
        """Tüm düşmanlar öldü mü?"""
        return not any(e['alive'] for e in self._enemies)

    def _get_observation(self) -> np.ndarray:
        """96-dim observation vector."""
        # Bot state
        self._obs_builder.self_state = CalypsoBotState(
            health=self._bot_health,
            armor=self._bot_armor,
            ammo_primary=self._bot_ammo,
            ammo_secondary=0.0,
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
            time_since_damage=0.5,
            current_tier=self.initial_tier / 6.0,
            alarm_level=self.alarm_level / 3.0,
            area_type=self.area_type / 2.0,
            combat_phase=min(1.0, self._time_since_alarm / 60.0)
        )

        # Enemy observations
        alive_enemies = [e for e in self._enemies if e['alive']]
        for i in range(3):
            if i < len(alive_enemies):
                enemy = alive_enemies[i]
                dist = np.linalg.norm(enemy['position'] - self._bot_position)
                angle = np.arctan2(
                    enemy['position'][1] - self._bot_position[1],
                    enemy['position'][0] - self._bot_position[0]
                ) / np.pi

                self._obs_builder.enemies[i] = CalypsoEnemyState(
                    distance=min(dist, 1.0),
                    angle=angle,
                    health_estimate=enemy['health'],
                    is_visible=1.0 if dist < 0.8 else 0.0,
                    is_in_cover=float(enemy.get('in_cover', False)),
                    threat_level=self._calculate_threat(enemy),
                    velocity_towards_me=0.0,
                    is_aiming_at_me=float(enemy.get('state') in ['panic_fire', 'suppressing']),
                    tier=enemy['tier'] / 6.0,
                    has_shield=float(enemy.get('has_shield', False)),
                    shield_hp=enemy.get('shield_hp', 0.0),
                    weapon_type=enemy.get('weapon', 0) / 7.0
                )
            else:
                self._obs_builder.enemies[i] = CalypsoEnemyState()

        # Environment
        spider_nearby = 0.0
        for spider in self._spider_mines:
            if spider['alive']:
                dist = np.linalg.norm(spider['position'] - self._bot_position)
                spider_nearby = max(spider_nearby, 1.0 - dist)

        boss_phase = 0.0
        if self._boss and self._boss['alive']:
            if self._boss['state'] == 'walking':
                boss_phase = 0.33
            elif self._boss['state'] in ['hammer_combo', 'leap']:
                boss_phase = 0.66
            elif self._boss['state'] == 'defense':
                boss_phase = 1.0

        self._obs_builder.environment = CalypsoEnvironmentState(
            spider_mine_nearby=spider_nearby,
            boss_phase=boss_phase,
            shield_enemies_count=sum(1 for e in self._enemies if e['alive'] and e.get('has_shield')) / 5.0,
            flank_route_available=1.0 if self.area_type == AreaType.WIDE else 0.5
        )

        # Tactical info
        self._obs_builder.tactical_info['suppression_threat'] = sum(
            1 for e in self._enemies
            if e['alive'] and e.get('role') == 'suppression'
        ) / 5.0

        self._obs_builder.tactical_info['flank_threat'] = sum(
            1 for e in self._enemies
            if e['alive'] and e.get('role') == 'flanker'
        ) / 5.0

        self._obs_builder.tactical_info['explosive_threat'] = spider_nearby

        self._obs_builder.tactical_info['boss_stun_window'] = (
            1.0 if self._boss and self._boss.get('is_stunned') else 0.0
        )

        return self._obs_builder.build()

    def _calculate_threat(self, enemy: Dict) -> float:
        """Düşman tehdit seviyesi."""
        threat = 0.3

        tier = enemy.get('tier', EnemyTier.TIER_1)
        if tier == EnemyTier.TIER_1:
            threat = 0.2
        elif tier == EnemyTier.TIER_2:
            threat = 0.5
        elif tier == EnemyTier.TIER_2_MARKSMAN:
            threat = 0.7
        elif tier == EnemyTier.TIER_2_SPECIAL:
            threat = 0.6

        if enemy.get('has_shield'):
            threat += 0.2

        return min(1.0, threat)

    def _get_info(self) -> Dict[str, Any]:
        """Ek bilgiler."""
        return {
            "step": self._step_count,
            "bot_health": self._bot_health,
            "bot_ammo": self._bot_ammo,
            "bot_kills": self._bot_kills,
            "enemies_alive": sum(1 for e in self._enemies if e['alive']),
            "damage_dealt": self._damage_dealt,
            "damage_taken": self._damage_taken,
            "total_reward": self._total_reward,
            "tier": self.initial_tier,
            "alarm_level": self.alarm_level,
            "area_type": self.area_type.name,
            "spider_mines": sum(1 for s in self._spider_mines if s['alive']),
            "boss_alive": self._boss['alive'] if self._boss else False
        }

    def render(self) -> Optional[np.ndarray]:
        """Render."""
        if self.render_mode == "human":
            print(f"\n=== CALYPSO Step {self._step_count} ===")
            print(f"Bot: HP={self._bot_health:.2f}, Ammo={self._bot_ammo:.2f}, "
                  f"Cover={self._bot_in_cover}")
            print(f"Tier: {self.initial_tier}, Alarm: {self.alarm_level}, "
                  f"Area: {self.area_type.name}")
            print(f"Kills: {self._bot_kills}, "
                  f"Enemies: {sum(1 for e in self._enemies if e['alive'])}")

            if self._boss and self._boss['alive']:
                print(f"BOSS: HP={self._boss['health']:.2f}, "
                      f"State={self._boss['state']}, "
                      f"Stunned={self._boss['is_stunned']}")

            print(f"Spider Mines: {sum(1 for s in self._spider_mines if s['alive'])}")
            print(f"Damage: Dealt={self._damage_dealt:.2f}, Taken={self._damage_taken:.2f}")
            print(f"Total Reward: {self._total_reward:.2f}")

        return None

    def close(self) -> None:
        """Cleanup."""
        pass


def make_calypso_env(**kwargs):
    """Environment factory."""
    return CalypsoMockEnv(**kwargs)
