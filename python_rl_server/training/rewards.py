"""
Reward Calculator
TÜBİTAK İP-2 AI Bot System

Reward shaping için fonksiyonlar.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import numpy as np


@dataclass
class RewardConfig:
    """Reward ağırlıkları konfigürasyonu."""
    kill_enemy: float = 10.0
    damage_dealt: float = 1.0  # per 10 HP
    damage_taken: float = -0.5  # per 10 HP
    death: float = -10.0
    survival_per_second: float = 0.1
    objective_progress: float = 5.0
    team_support: float = 2.0
    cover_usage: float = 0.5
    headshot_bonus: float = 3.0
    assist: float = 2.0
    reload_in_cover: float = 0.2
    unnecessary_reload: float = -0.1
    ammo_waste: float = -0.05
    flank_success: float = 3.0


class RewardCalculator:
    """
    Reward hesaplayıcı.

    Farklı olaylar için reward değerleri hesaplar.
    Reward shaping ile agent'ın öğrenmesini hızlandırır.
    """

    def __init__(self, config: Optional[RewardConfig] = None):
        """
        Args:
            config: Reward ağırlıkları
        """
        self.config = config or RewardConfig()
        self._episode_stats = self._reset_stats()

    def _reset_stats(self) -> Dict:
        """Episode istatistiklerini sıfırla."""
        return {
            "kills": 0,
            "deaths": 0,
            "damage_dealt": 0.0,
            "damage_taken": 0.0,
            "shots_fired": 0,
            "shots_hit": 0,
            "cover_time": 0.0,
            "total_reward": 0.0
        }

    def reset(self) -> None:
        """Episode başında çağır."""
        self._episode_stats = self._reset_stats()

    def calculate_reward(
        self,
        event: str,
        value: float = 1.0,
        context: Optional[Dict] = None
    ) -> float:
        """
        Olay bazlı reward hesapla.

        Args:
            event: Olay tipi ("kill", "damage_dealt", "death", vs.)
            value: Olay değeri (opsiyonel miktar)
            context: Ek context bilgisi

        Returns:
            Hesaplanan reward değeri
        """
        context = context or {}
        reward = 0.0

        if event == "kill":
            reward = self.config.kill_enemy
            self._episode_stats["kills"] += 1

            # Headshot bonus
            if context.get("headshot", False):
                reward += self.config.headshot_bonus

        elif event == "assist":
            reward = self.config.assist

        elif event == "damage_dealt":
            # value = hasar miktarı (0-1 normalized)
            reward = self.config.damage_dealt * (value * 10)
            self._episode_stats["damage_dealt"] += value

        elif event == "damage_taken":
            reward = self.config.damage_taken * (value * 10)
            self._episode_stats["damage_taken"] += value

        elif event == "death":
            reward = self.config.death
            self._episode_stats["deaths"] += 1

        elif event == "survival":
            # value = geçen süre (saniye)
            reward = self.config.survival_per_second * value

        elif event == "objective_progress":
            # value = ilerleme miktarı (0-1)
            reward = self.config.objective_progress * value

        elif event == "team_support":
            reward = self.config.team_support

        elif event == "cover_enter":
            reward = self.config.cover_usage
            self._episode_stats["cover_time"] += 1

        elif event == "reload":
            if context.get("in_cover", False):
                reward = self.config.reload_in_cover
            elif context.get("ammo_full", False):
                reward = self.config.unnecessary_reload

        elif event == "shot_fired":
            self._episode_stats["shots_fired"] += 1
            if not context.get("hit", False) and not context.get("suppression", False):
                reward = self.config.ammo_waste

        elif event == "shot_hit":
            self._episode_stats["shots_hit"] += 1

        elif event == "flank_success":
            reward = self.config.flank_success

        self._episode_stats["total_reward"] += reward
        return reward

    def calculate_step_reward(
        self,
        prev_state: Dict,
        action: int,
        curr_state: Dict,
        done: bool
    ) -> float:
        """
        State geçişi bazlı toplam reward hesapla.

        Args:
            prev_state: Önceki state dict
            action: Alınan aksiyon
            curr_state: Mevcut state dict
            done: Episode bitti mi

        Returns:
            Toplam step reward
        """
        total_reward = 0.0

        # Hasar verdiyse
        damage_diff = curr_state.get("damage_dealt", 0) - prev_state.get("damage_dealt", 0)
        if damage_diff > 0:
            total_reward += self.calculate_reward("damage_dealt", damage_diff)

        # Hasar aldıysa
        health_diff = prev_state.get("health", 1) - curr_state.get("health", 1)
        if health_diff > 0:
            total_reward += self.calculate_reward("damage_taken", health_diff)

        # Kill aldıysa
        kills_diff = curr_state.get("kills", 0) - prev_state.get("kills", 0)
        for _ in range(int(kills_diff)):
            total_reward += self.calculate_reward("kill")

        # Öldüyse
        if done and curr_state.get("health", 1) <= 0:
            total_reward += self.calculate_reward("death")

        # Hayatta kalma bonus
        if not done:
            total_reward += self.calculate_reward("survival", 0.033)  # ~30 FPS

        # Cover kullanımı
        if curr_state.get("in_cover", False) and not prev_state.get("in_cover", False):
            total_reward += self.calculate_reward("cover_enter")

        return total_reward

    def get_episode_stats(self) -> Dict:
        """Episode istatistiklerini döndür."""
        stats = self._episode_stats.copy()

        # Accuracy hesapla
        if stats["shots_fired"] > 0:
            stats["accuracy"] = stats["shots_hit"] / stats["shots_fired"]
        else:
            stats["accuracy"] = 0.0

        # K/D hesapla
        if stats["deaths"] > 0:
            stats["kd_ratio"] = stats["kills"] / stats["deaths"]
        else:
            stats["kd_ratio"] = float(stats["kills"])

        return stats

    def get_reward_breakdown(self) -> Dict[str, float]:
        """Her reward türünün toplam katkısını döndür."""
        return {
            "kills": self._episode_stats["kills"] * self.config.kill_enemy,
            "damage_dealt": self._episode_stats["damage_dealt"] * self.config.damage_dealt * 10,
            "damage_taken": self._episode_stats["damage_taken"] * self.config.damage_taken * 10,
            "deaths": self._episode_stats["deaths"] * self.config.death,
            "total": self._episode_stats["total_reward"]
        }
