"""
Difficulty Manager
TÜBİTAK İP-2 AI Bot System

Adaptif zorluk yönetimi - DDA (Dynamic Difficulty Adjustment)
Referans: Pfau et al. (2020) - Enemy within DDA
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np
import yaml

from .player_tracker import PlayerPerformanceTracker, PlayerMetrics


@dataclass
class BotDifficultyParams:
    """Bot zorluk parametreleri."""
    health: int = 100
    accuracy: float = 0.5
    reaction_time: float = 0.5
    aggression: float = 0.5
    sight_range: float = 2000
    hearing_range: float = 1000
    cover_usage_chance: float = 0.5
    flank_chance: float = 0.3


@dataclass
class DifficultyLevel:
    """Zorluk seviyesi tanımı."""
    level: int
    name: str
    name_en: str
    params: BotDifficultyParams


class DifficultyManager:
    """
    Adaptif Zorluk Yöneticisi.

    Oyuncu performansına göre zorluk seviyesini dinamik ayarlar.
    Yumuşak geçişler (smooth transitions) sağlar.
    """

    # 7 Zorluk seviyesi
    DIFFICULTY_LEVELS = {
        1: DifficultyLevel(
            level=1, name="Yolcu", name_en="Passenger",
            params=BotDifficultyParams(
                health=50, accuracy=0.20, reaction_time=1.0,
                aggression=0.10, sight_range=1000, hearing_range=500,
                cover_usage_chance=0.3, flank_chance=0.1
            )
        ),
        2: DifficultyLevel(
            level=2, name="Mürettebat", name_en="Crew",
            params=BotDifficultyParams(
                health=75, accuracy=0.40, reaction_time=0.7,
                aggression=0.30, sight_range=1500, hearing_range=750,
                cover_usage_chance=0.4, flank_chance=0.2
            )
        ),
        3: DifficultyLevel(
            level=3, name="Gemi Muhafızı", name_en="Ship Guard",
            params=BotDifficultyParams(
                health=100, accuracy=0.60, reaction_time=0.5,
                aggression=0.50, sight_range=2000, hearing_range=1000,
                cover_usage_chance=0.5, flank_chance=0.3
            )
        ),
        4: DifficultyLevel(
            level=4, name="Gemi Polisi", name_en="Ship Police",
            params=BotDifficultyParams(
                health=120, accuracy=0.70, reaction_time=0.4,
                aggression=0.60, sight_range=2200, hearing_range=1100,
                cover_usage_chance=0.6, flank_chance=0.4
            )
        ),
        5: DifficultyLevel(
            level=5, name="Koruma", name_en="Bodyguard",
            params=BotDifficultyParams(
                health=150, accuracy=0.80, reaction_time=0.3,
                aggression=0.70, sight_range=2500, hearing_range=1250,
                cover_usage_chance=0.7, flank_chance=0.5
            )
        ),
        6: DifficultyLevel(
            level=6, name="Sahil Güvenlik", name_en="Coast Guard",
            params=BotDifficultyParams(
                health=175, accuracy=0.85, reaction_time=0.25,
                aggression=0.80, sight_range=2750, hearing_range=1375,
                cover_usage_chance=0.8, flank_chance=0.6
            )
        ),
        7: DifficultyLevel(
            level=7, name="Özel Kuvvetler", name_en="Special Forces",
            params=BotDifficultyParams(
                health=200, accuracy=0.95, reaction_time=0.15,
                aggression=0.90, sight_range=3000, hearing_range=1500,
                cover_usage_chance=0.9, flank_chance=0.7
            )
        )
    }

    def __init__(
        self,
        enabled: bool = True,
        adjustment_rate: float = 0.1,
        min_difficulty: float = 0.1,
        max_difficulty: float = 1.0,
        config_path: Optional[str] = None
    ):
        """
        Args:
            enabled: DDA aktif mi?
            adjustment_rate: Zorluk değişim hızı (0-1, düşük = yavaş geçiş)
            min_difficulty: Minimum zorluk (0-1)
            max_difficulty: Maksimum zorluk (0-1)
            config_path: Opsiyonel config dosyası yolu
        """
        self.enabled = enabled
        self.adjustment_rate = adjustment_rate
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty

        # Config'den yükle
        if config_path:
            self._load_config(config_path)

        # Player trackers
        self._player_trackers: Dict[str, PlayerPerformanceTracker] = {}

        # Current difficulty per player (0-1 continuous)
        self._current_difficulty: Dict[str, float] = {}

        # Trend tracking
        self._difficulty_history: Dict[str, list] = {}

    def _load_config(self, config_path: str) -> None:
        """Config dosyasından ayarları yükle."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            dda_config = config.get("adaptive_difficulty", {})
            self.enabled = dda_config.get("enabled", self.enabled)
            self.adjustment_rate = dda_config.get("adjustment_rate", self.adjustment_rate)
            self.min_difficulty = dda_config.get("min_difficulty", self.min_difficulty)
            self.max_difficulty = dda_config.get("max_difficulty", self.max_difficulty)

        except Exception as e:
            print(f"[DifficultyManager] Config load error: {e}")

    def register_player(self, player_id: str) -> None:
        """Yeni oyuncu kaydet."""
        if player_id not in self._player_trackers:
            self._player_trackers[player_id] = PlayerPerformanceTracker(player_id)
            self._current_difficulty[player_id] = 0.5  # Orta başla
            self._difficulty_history[player_id] = []

    def get_tracker(self, player_id: str) -> PlayerPerformanceTracker:
        """Oyuncu tracker'ını al."""
        if player_id not in self._player_trackers:
            self.register_player(player_id)
        return self._player_trackers[player_id]

    def update_difficulty(self, player_id: str) -> float:
        """
        Oyuncu için zorluk seviyesini güncelle.

        Args:
            player_id: Oyuncu ID'si

        Returns:
            Yeni zorluk seviyesi (0-1)
        """
        if not self.enabled:
            return self._current_difficulty.get(player_id, 0.5)

        if player_id not in self._player_trackers:
            self.register_player(player_id)

        tracker = self._player_trackers[player_id]
        current = self._current_difficulty[player_id]

        # Skill score hesapla
        skill_score = tracker.calculate_skill_score()

        # Target difficulty = skill score
        target = skill_score

        # Smooth transition (exponential moving average)
        new_difficulty = current + self.adjustment_rate * (target - current)

        # Clamp
        new_difficulty = np.clip(new_difficulty, self.min_difficulty, self.max_difficulty)

        self._current_difficulty[player_id] = new_difficulty
        self._difficulty_history[player_id].append(new_difficulty)

        return new_difficulty

    def get_current_difficulty(self, player_id: str) -> float:
        """Mevcut zorluk seviyesini al (0-1)."""
        return self._current_difficulty.get(player_id, 0.5)

    def get_difficulty_level(self, player_id: str) -> int:
        """Mevcut zorluk seviyesini discrete olarak al (1-7)."""
        difficulty = self.get_current_difficulty(player_id)
        # 0-1 -> 1-7
        level = int(difficulty * 6) + 1
        return np.clip(level, 1, 7)

    def get_bot_params(self, player_id: str) -> BotDifficultyParams:
        """Mevcut zorluk için bot parametrelerini al."""
        level = self.get_difficulty_level(player_id)
        return self.DIFFICULTY_LEVELS[level].params

    def get_interpolated_params(self, player_id: str) -> BotDifficultyParams:
        """
        Smooth interpolated bot parametreleri.

        Discrete seviyeler arası interpolasyon yapar.
        """
        difficulty = self.get_current_difficulty(player_id)

        # Hangi iki seviye arasındayız?
        level_float = difficulty * 6 + 1  # 1-7
        lower_level = max(1, int(level_float))
        upper_level = min(7, lower_level + 1)

        t = level_float - lower_level  # Interpolation factor

        lower_params = self.DIFFICULTY_LEVELS[lower_level].params
        upper_params = self.DIFFICULTY_LEVELS[upper_level].params

        # Interpolate each parameter
        return BotDifficultyParams(
            health=int(lower_params.health + t * (upper_params.health - lower_params.health)),
            accuracy=lower_params.accuracy + t * (upper_params.accuracy - lower_params.accuracy),
            reaction_time=lower_params.reaction_time + t * (upper_params.reaction_time - lower_params.reaction_time),
            aggression=lower_params.aggression + t * (upper_params.aggression - lower_params.aggression),
            sight_range=lower_params.sight_range + t * (upper_params.sight_range - lower_params.sight_range),
            hearing_range=lower_params.hearing_range + t * (upper_params.hearing_range - lower_params.hearing_range),
            cover_usage_chance=lower_params.cover_usage_chance + t * (upper_params.cover_usage_chance - lower_params.cover_usage_chance),
            flank_chance=lower_params.flank_chance + t * (upper_params.flank_chance - lower_params.flank_chance)
        )

    def set_difficulty(self, player_id: str, level: int) -> None:
        """Manuel zorluk ayarla (1-7)."""
        if player_id not in self._current_difficulty:
            self.register_player(player_id)

        # Level -> 0-1
        difficulty = (level - 1) / 6.0
        self._current_difficulty[player_id] = np.clip(difficulty, 0.0, 1.0)

    def get_difficulty_trend(self, player_id: str) -> str:
        """Zorluk trendi (STABLE, INCREASING, DECREASING)."""
        history = self._difficulty_history.get(player_id, [])

        if len(history) < 10:
            return "STABLE"

        recent = history[-10:]
        slope = np.polyfit(range(len(recent)), recent, 1)[0]

        if slope > 0.01:
            return "INCREASING"
        elif slope < -0.01:
            return "DECREASING"
        return "STABLE"

    def get_difficulty_info(self, player_id: str) -> Dict:
        """Zorluk bilgilerini dict olarak döndür."""
        level = self.get_difficulty_level(player_id)
        level_info = self.DIFFICULTY_LEVELS[level]
        params = self.get_interpolated_params(player_id)

        return {
            "player_id": player_id,
            "difficulty_continuous": self.get_current_difficulty(player_id),
            "difficulty_level": level,
            "difficulty_name": level_info.name,
            "difficulty_name_en": level_info.name_en,
            "trend": self.get_difficulty_trend(player_id),
            "bot_params": {
                "health": params.health,
                "accuracy": params.accuracy,
                "reaction_time": params.reaction_time,
                "aggression": params.aggression,
                "sight_range": params.sight_range,
                "hearing_range": params.hearing_range,
                "cover_usage_chance": params.cover_usage_chance,
                "flank_chance": params.flank_chance
            }
        }
