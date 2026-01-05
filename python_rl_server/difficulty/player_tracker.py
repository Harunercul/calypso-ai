"""
Player Performance Tracker
TÜBİTAK İP-2 AI Bot System

Oyuncu performansını takip eder ve skill skoru hesaplar.
Referans: Pfau et al. (2020) - Deep player behavior models for DDA
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import numpy as np


@dataclass
class PlayerMetrics:
    """Oyuncu performans metrikleri."""
    accuracy_ratio: float = 0.0
    kill_death_ratio: float = 1.0
    average_lifespan: float = 60.0
    headshot_ratio: float = 0.0
    damage_per_minute: float = 0.0
    objectives_completed: int = 0
    reaction_time_avg: float = 0.5

    # Recent events
    recent_kills: int = 0
    recent_deaths: int = 0
    recent_damage_dealt: float = 0.0
    recent_damage_taken: float = 0.0


class PlayerPerformanceTracker:
    """
    Oyuncu performans takipçisi.

    Son X saniyedeki performansı izler ve skill skoru hesaplar.
    DDA sistemi bu skoru kullanarak zorluk seviyesini ayarlar.
    """

    def __init__(
        self,
        player_id: str,
        window_size: int = 60,  # Değerlendirme penceresi (saniye)
        min_samples: int = 10,   # Minimum sample sayısı
        metric_weights: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            player_id: Oyuncu ID'si
            window_size: Performans değerlendirme penceresi (saniye)
            min_samples: Değerlendirme için minimum sample
            metric_weights: Metrik ağırlıkları
        """
        self.player_id = player_id
        self.window_size = window_size
        self.min_samples = min_samples

        # Default weights
        self.metric_weights = metric_weights or {
            "accuracy_ratio": 0.25,
            "kill_death_ratio": 0.30,
            "average_lifespan": 0.20,
            "headshot_ratio": 0.10,
            "damage_per_minute": 0.15
        }

        # Event buffers (timestamp, value)
        self._shots_fired = deque(maxlen=1000)
        self._shots_hit = deque(maxlen=1000)
        self._kills = deque(maxlen=100)
        self._deaths = deque(maxlen=100)
        self._lifespans = deque(maxlen=50)
        self._headshots = deque(maxlen=100)
        self._damage_dealt = deque(maxlen=500)
        self._damage_taken = deque(maxlen=500)
        self._reaction_times = deque(maxlen=100)
        self._objectives = deque(maxlen=50)

        # Current life tracking
        self._life_start_time: Optional[float] = None
        self._current_metrics = PlayerMetrics()

    def record_shot(self, hit: bool, headshot: bool = False) -> None:
        """Atış kaydet."""
        now = time.time()
        self._shots_fired.append((now, 1))

        if hit:
            self._shots_hit.append((now, 1))

            if headshot:
                self._headshots.append((now, 1))

    def record_kill(self) -> None:
        """Kill kaydet."""
        self._kills.append((time.time(), 1))

    def record_death(self) -> None:
        """Ölüm kaydet."""
        now = time.time()
        self._deaths.append((now, 1))

        # Lifespan hesapla
        if self._life_start_time is not None:
            lifespan = now - self._life_start_time
            self._lifespans.append((now, lifespan))

        self._life_start_time = None

    def record_spawn(self) -> None:
        """Yeni hayat başlangıcı."""
        self._life_start_time = time.time()

    def record_damage_dealt(self, amount: float) -> None:
        """Verilen hasar kaydet."""
        self._damage_dealt.append((time.time(), amount))

    def record_damage_taken(self, amount: float) -> None:
        """Alınan hasar kaydet."""
        self._damage_taken.append((time.time(), amount))

    def record_reaction_time(self, reaction_time: float) -> None:
        """Tepki süresi kaydet."""
        self._reaction_times.append((time.time(), reaction_time))

    def record_objective(self) -> None:
        """Objective tamamlama kaydet."""
        self._objectives.append((time.time(), 1))

    def _get_window_sum(self, buffer: deque, window: float) -> float:
        """Son X saniyedeki değerlerin toplamı."""
        now = time.time()
        cutoff = now - window
        return sum(v for t, v in buffer if t > cutoff)

    def _get_window_count(self, buffer: deque, window: float) -> int:
        """Son X saniyedeki event sayısı."""
        now = time.time()
        cutoff = now - window
        return sum(1 for t, v in buffer if t > cutoff)

    def _get_window_avg(self, buffer: deque, window: float) -> float:
        """Son X saniyedeki değerlerin ortalaması."""
        now = time.time()
        cutoff = now - window
        values = [v for t, v in buffer if t > cutoff]
        return np.mean(values) if values else 0.0

    def calculate_metrics(self) -> PlayerMetrics:
        """Mevcut metrikleri hesapla."""
        window = self.window_size

        # Accuracy
        shots = self._get_window_count(self._shots_fired, window)
        hits = self._get_window_count(self._shots_hit, window)
        accuracy = hits / shots if shots > 0 else 0.0

        # K/D
        kills = self._get_window_count(self._kills, window)
        deaths = self._get_window_count(self._deaths, window)
        kd = kills / deaths if deaths > 0 else float(kills)

        # Average lifespan
        avg_lifespan = self._get_window_avg(self._lifespans, window)
        if avg_lifespan == 0:
            avg_lifespan = 60.0  # Default

        # Headshot ratio
        headshots = self._get_window_count(self._headshots, window)
        hs_ratio = headshots / hits if hits > 0 else 0.0

        # DPM
        damage = self._get_window_sum(self._damage_dealt, window)
        dpm = (damage / window) * 60 if window > 0 else 0.0

        # Objectives
        objectives = self._get_window_count(self._objectives, window)

        # Reaction time
        avg_reaction = self._get_window_avg(self._reaction_times, window)
        if avg_reaction == 0:
            avg_reaction = 0.5  # Default

        # Recent events (son 30 saniye)
        recent_window = min(30, window)
        recent_kills = self._get_window_count(self._kills, recent_window)
        recent_deaths = self._get_window_count(self._deaths, recent_window)
        recent_dmg_dealt = self._get_window_sum(self._damage_dealt, recent_window)
        recent_dmg_taken = self._get_window_sum(self._damage_taken, recent_window)

        self._current_metrics = PlayerMetrics(
            accuracy_ratio=accuracy,
            kill_death_ratio=kd,
            average_lifespan=avg_lifespan,
            headshot_ratio=hs_ratio,
            damage_per_minute=dpm,
            objectives_completed=objectives,
            reaction_time_avg=avg_reaction,
            recent_kills=recent_kills,
            recent_deaths=recent_deaths,
            recent_damage_dealt=recent_dmg_dealt,
            recent_damage_taken=recent_dmg_taken
        )

        return self._current_metrics

    def calculate_skill_score(self) -> float:
        """
        Oyuncu skill skoru hesapla (0-1 arası).

        Bu skor DDA sisteminin ana girdisi.
        """
        metrics = self.calculate_metrics()

        # Normalize each metric to 0-1
        scores = {}

        # Accuracy (0-1 zaten)
        scores["accuracy_ratio"] = min(metrics.accuracy_ratio, 1.0)

        # K/D (0 -> 0, 2+ -> 1)
        scores["kill_death_ratio"] = min(metrics.kill_death_ratio / 2.0, 1.0)

        # Lifespan (30s -> 0.5, 120s+ -> 1)
        scores["average_lifespan"] = min(metrics.average_lifespan / 120.0, 1.0)

        # Headshot ratio (0-1 zaten)
        scores["headshot_ratio"] = min(metrics.headshot_ratio, 1.0)

        # DPM (normalize to typical range)
        scores["damage_per_minute"] = min(metrics.damage_per_minute / 500.0, 1.0)

        # Weighted average
        total_weight = sum(self.metric_weights.values())
        skill_score = sum(
            scores.get(metric, 0) * weight
            for metric, weight in self.metric_weights.items()
        ) / total_weight

        return np.clip(skill_score, 0.0, 1.0)

    def get_metrics(self) -> PlayerMetrics:
        """Mevcut metrikleri döndür."""
        return self._current_metrics

    def get_metrics_dict(self) -> Dict:
        """Metrikleri dict olarak döndür."""
        metrics = self.calculate_metrics()
        return {
            "player_id": self.player_id,
            "accuracy_ratio": metrics.accuracy_ratio,
            "kill_death_ratio": metrics.kill_death_ratio,
            "average_lifespan": metrics.average_lifespan,
            "headshot_ratio": metrics.headshot_ratio,
            "damage_per_minute": metrics.damage_per_minute,
            "objectives_completed": metrics.objectives_completed,
            "reaction_time_avg": metrics.reaction_time_avg,
            "skill_score": self.calculate_skill_score()
        }
