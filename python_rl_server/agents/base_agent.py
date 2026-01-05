"""
Base Agent - Abstract base class for all agents
TÜBİTAK İP-2 AI Bot System
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
import numpy as np


class BaseAgent(ABC):
    """
    Tüm agent'ların inherit edeceği abstract base class.

    Referans: Uludağlı & Oğuz (2023) - NPC Decision-Making Taxonomy
    """

    def __init__(self, name: str, observation_dim: int = 64, action_dim: int = 8):
        """
        Args:
            name: Agent ismi
            observation_dim: Observation vector boyutu
            action_dim: Action space boyutu (discrete actions)
        """
        self.name = name
        self.observation_dim = observation_dim
        self.action_dim = action_dim
        self.is_training = False
        self._step_count = 0

    @abstractmethod
    def select_action(
        self,
        observation: np.ndarray,
        deterministic: bool = False
    ) -> Tuple[int, Dict[str, float]]:
        """
        Observation'a göre aksiyon seç.

        Args:
            observation: 64-dim normalized observation vector
            deterministic: True ise exploitation, False ise exploration

        Returns:
            action: Seçilen aksiyon (0-7 arası integer)
            info: Ek bilgiler (utility scores vs.)
        """
        pass

    @abstractmethod
    def update(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool
    ) -> Dict[str, float]:
        """
        Agent'ı güncelle (training).

        Args:
            observation: Mevcut observation
            action: Alınan aksiyon
            reward: Alınan reward
            next_observation: Sonraki observation
            done: Episode bitti mi?

        Returns:
            metrics: Training metrikleri (loss vs.)
        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """Model'i kaydet."""
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        """Model'i yükle."""
        pass

    def set_training_mode(self, training: bool) -> None:
        """Training/inference mode ayarla."""
        self.is_training = training

    def reset(self) -> None:
        """Episode başında reset."""
        self._step_count = 0

    def step(self) -> None:
        """Her adımda çağrılır."""
        self._step_count += 1

    @property
    def step_count(self) -> int:
        """Toplam adım sayısı."""
        return self._step_count

    def get_action_name(self, action: int) -> str:
        """Aksiyon numarasından isim döndür."""
        action_names = {
            0: "IDLE",
            1: "ATTACK",
            2: "TAKE_COVER",
            3: "FLEE",
            4: "RELOAD",
            5: "PATROL",
            6: "INVESTIGATE",
            7: "SUPPORT",
            8: "FLANK"
        }
        return action_names.get(action, "UNKNOWN")
