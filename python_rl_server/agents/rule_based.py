"""
Rule-Based Agent - Karşılaştırma için klasik kural tabanlı bot
TÜBİTAK İP-2 AI Bot System

Bu agent RL agent ile karşılaştırma yapmak için kullanılacak.
Demo'da "Rule-based vs RL" senaryosunda gösterilecek.

Referans: Hong et al. (2023) - GOBT Utility AI yaklaşımı
"""

from typing import Dict, Tuple
import numpy as np

from .base_agent import BaseAgent


class RuleBasedAgent(BaseAgent):
    """
    Kural tabanlı bot - Utility AI benzeri yaklaşım.

    Her aksiyon için bir utility skoru hesaplar ve
    en yüksek skorlu aksiyonu seçer.
    """

    # Aksiyon sabitleri
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
        name: str = "RuleBasedAgent",
        observation_dim: int = 64,
        action_dim: int = 9,
        aggression: float = 0.5,
        caution: float = 0.5,
        team_focus: float = 0.5
    ):
        """
        Args:
            name: Agent ismi
            aggression: Saldırganlık seviyesi (0-1)
            caution: Temkinlilik seviyesi (0-1)
            team_focus: Takım odaklılık (0-1)
        """
        super().__init__(name, observation_dim, action_dim)

        self.aggression = aggression
        self.caution = caution
        self.team_focus = team_focus

    def select_action(
        self,
        observation: np.ndarray,
        deterministic: bool = True
    ) -> Tuple[int, Dict[str, float]]:
        """
        Utility skorlarına göre aksiyon seç.

        Observation yapısı (64 dim):
        - [0-15]: Bot self state
        - [16-39]: 3 düşman (her biri 8 dim)
        - [40-55]: Environment state
        - [56-63]: Team state
        """
        # Observation'dan bilgileri çıkar
        obs = observation.flatten()

        # Self state
        self_health = obs[0] if len(obs) > 0 else 1.0
        self_ammo = obs[2] if len(obs) > 2 else 1.0
        is_in_cover = obs[13] if len(obs) > 13 else 0.0
        is_reloading = obs[14] if len(obs) > 14 else 0.0

        # En yakın düşman bilgisi (index 16-23)
        enemy_distance = obs[16] if len(obs) > 16 else 1.0
        enemy_visible = obs[19] if len(obs) > 19 else 0.0
        enemy_threat = obs[21] if len(obs) > 21 else 0.0
        enemy_aiming_at_me = obs[23] if len(obs) > 23 else 0.0

        # Çevre - siper mesafesi (index 40-41)
        cover_distance = obs[40] if len(obs) > 40 else 1.0

        # Takım durumu (index 56-63)
        team_health = obs[56] if len(obs) > 56 else 1.0
        support_needed = obs[63] if len(obs) > 63 else 0.0

        # Her aksiyon için utility hesapla
        utilities = {}

        # IDLE - Düşman yoksa veya herşey iyi
        utilities["IDLE"] = self._utility_idle(
            enemy_visible, self_health, is_in_cover
        )

        # ATTACK - Düşman görünür ve saldırabilir durumdayız
        utilities["ATTACK"] = self._utility_attack(
            enemy_visible, enemy_distance, self_health, self_ammo,
            enemy_threat, self.aggression
        )

        # TAKE_COVER - Tehlike altındayız ve siper yakın
        utilities["TAKE_COVER"] = self._utility_take_cover(
            enemy_aiming_at_me, self_health, is_in_cover,
            cover_distance, self.caution
        )

        # FLEE - Can çok düşük
        utilities["FLEE"] = self._utility_flee(
            self_health, enemy_threat, enemy_distance, self.caution
        )

        # RELOAD - Mermi az
        utilities["RELOAD"] = self._utility_reload(
            self_ammo, is_reloading, enemy_distance, is_in_cover
        )

        # PATROL - Düşman yok, keşif yap
        utilities["PATROL"] = self._utility_patrol(
            enemy_visible, self_health
        )

        # INVESTIGATE - Ses duyuldu ama düşman görünmüyor
        utilities["INVESTIGATE"] = self._utility_investigate(
            enemy_visible, enemy_distance
        )

        # SUPPORT - Takım arkadaşı tehlikede
        utilities["SUPPORT"] = self._utility_support(
            support_needed, team_health, self_health, self.team_focus
        )

        # FLANK - Yan atak fırsatı
        utilities["FLANK"] = self._utility_flank(
            enemy_visible, enemy_distance, is_in_cover,
            self_health, self.aggression
        )

        # En yüksek utility'yi bul
        action_map = {
            "IDLE": self.ACTION_IDLE,
            "ATTACK": self.ACTION_ATTACK,
            "TAKE_COVER": self.ACTION_TAKE_COVER,
            "FLEE": self.ACTION_FLEE,
            "RELOAD": self.ACTION_RELOAD,
            "PATROL": self.ACTION_PATROL,
            "INVESTIGATE": self.ACTION_INVESTIGATE,
            "SUPPORT": self.ACTION_SUPPORT,
            "FLANK": self.ACTION_FLANK
        }

        if deterministic:
            # En yüksek utility
            best_action_name = max(utilities, key=utilities.get)
        else:
            # Softmax ile stochastic seçim
            utility_values = np.array(list(utilities.values()))
            probs = self._softmax(utility_values, temperature=0.5)
            action_names = list(utilities.keys())
            best_action_name = np.random.choice(action_names, p=probs)

        action = action_map[best_action_name]

        # Info dict - utility skorları
        info = {f"utility_{k}": v for k, v in utilities.items()}
        info["selected_action"] = best_action_name

        self.step()

        return action, info

    def _utility_idle(
        self,
        enemy_visible: float,
        self_health: float,
        is_in_cover: float
    ) -> float:
        """IDLE utility - bekle."""
        # Düşman yoksa ve güvendeyse idle yüksek
        score = 0.3
        if enemy_visible < 0.5:
            score += 0.4
        if is_in_cover > 0.5 and self_health > 0.8:
            score += 0.2
        return min(score, 1.0)

    def _utility_attack(
        self,
        enemy_visible: float,
        enemy_distance: float,
        self_health: float,
        self_ammo: float,
        enemy_threat: float,
        aggression: float
    ) -> float:
        """ATTACK utility - saldır."""
        if enemy_visible < 0.5 or self_ammo < 0.1:
            return 0.0

        score = 0.0

        # Düşman görünürse base skor
        score += 0.3 * enemy_visible

        # Mesafe - yakınsa daha iyi
        score += 0.2 * (1 - enemy_distance)

        # Sağlık durumu
        score += 0.2 * self_health

        # Mermi durumu
        score += 0.1 * self_ammo

        # Agresiflik personality
        score += 0.2 * aggression

        # Tehdit düşükse bonus
        if enemy_threat < 0.3:
            score += 0.1

        return min(score, 1.0)

    def _utility_take_cover(
        self,
        enemy_aiming: float,
        self_health: float,
        is_in_cover: float,
        cover_distance: float,
        caution: float
    ) -> float:
        """TAKE_COVER utility - siper al."""
        # Zaten siperdeysek düşük
        if is_in_cover > 0.5:
            return 0.1

        score = 0.0

        # Düşman bize nişan alıyorsa yüksek
        score += 0.3 * enemy_aiming

        # Can düşükse yüksek
        score += 0.3 * (1 - self_health)

        # Siper yakınsa bonus
        score += 0.2 * (1 - cover_distance)

        # Temkinli personality
        score += 0.2 * caution

        return min(score, 1.0)

    def _utility_flee(
        self,
        self_health: float,
        enemy_threat: float,
        enemy_distance: float,
        caution: float
    ) -> float:
        """FLEE utility - kaç."""
        score = 0.0

        # Can çok düşükse kaç
        if self_health < 0.2:
            score += 0.5
        elif self_health < 0.4:
            score += 0.3

        # Tehdit yüksekse kaç
        score += 0.3 * enemy_threat

        # Düşman çok yakınsa kaç
        if enemy_distance < 0.2:
            score += 0.2

        # Temkinlilik
        score += 0.1 * caution

        return min(score, 1.0)

    def _utility_reload(
        self,
        self_ammo: float,
        is_reloading: float,
        enemy_distance: float,
        is_in_cover: float
    ) -> float:
        """RELOAD utility - mermi doldur."""
        # Zaten dolduruyorsak düşük
        if is_reloading > 0.5:
            return 0.0

        # Mermi tamsa düşük
        if self_ammo > 0.8:
            return 0.0

        score = 0.0

        # Mermi azsa yüksek
        score += 0.5 * (1 - self_ammo)

        # Siperdeysek bonus
        if is_in_cover > 0.5:
            score += 0.3

        # Düşman uzaksa bonus
        score += 0.2 * enemy_distance

        return min(score, 1.0)

    def _utility_patrol(
        self,
        enemy_visible: float,
        self_health: float
    ) -> float:
        """PATROL utility - devriye gez."""
        # Düşman varsa patrol düşük
        if enemy_visible > 0.5:
            return 0.0

        score = 0.3

        # Sağlıklıysak patrol
        score += 0.3 * self_health

        # Düşman görünmüyorsa bonus
        score += 0.4 * (1 - enemy_visible)

        return min(score, 1.0)

    def _utility_investigate(
        self,
        enemy_visible: float,
        enemy_distance: float
    ) -> float:
        """INVESTIGATE utility - araştır."""
        # Düşman tam görünüyorsa investigate düşük
        if enemy_visible > 0.8:
            return 0.1

        score = 0.0

        # Düşman biraz görünüyor ama tam değil
        if 0.2 < enemy_visible < 0.8:
            score += 0.5

        # Düşman uzakta
        score += 0.3 * enemy_distance

        return min(score, 1.0)

    def _utility_support(
        self,
        support_needed: float,
        team_health: float,
        self_health: float,
        team_focus: float
    ) -> float:
        """SUPPORT utility - takım arkadaşına yardım."""
        score = 0.0

        # Destek çağrısı varsa
        score += 0.4 * support_needed

        # Takım canı düşükse
        score += 0.2 * (1 - team_health)

        # Kendi canımız iyiyse yardım edebiliriz
        score += 0.2 * self_health

        # Takım odaklılık
        score += 0.2 * team_focus

        return min(score, 1.0)

    def _utility_flank(
        self,
        enemy_visible: float,
        enemy_distance: float,
        is_in_cover: float,
        self_health: float,
        aggression: float
    ) -> float:
        """FLANK utility - yan atak."""
        # Düşman görünmüyorsa flank düşük
        if enemy_visible < 0.3:
            return 0.0

        score = 0.0

        # Düşman görünür ve orta mesafede
        if 0.3 < enemy_distance < 0.7:
            score += 0.3

        # Siperdeysek flank fırsatı
        if is_in_cover > 0.5:
            score += 0.2

        # Sağlıklıysak risk alabiliriz
        score += 0.2 * self_health

        # Agresiflik
        score += 0.3 * aggression

        return min(score, 1.0)

    def _softmax(self, x: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        """Softmax with temperature."""
        x = x / temperature
        exp_x = np.exp(x - np.max(x))  # Numerical stability
        return exp_x / exp_x.sum()

    def update(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool
    ) -> Dict[str, float]:
        """Rule-based agent update yapmaz."""
        return {"reward": reward}

    def save(self, path: str) -> None:
        """Rule-based agent için sadece parametreleri kaydet."""
        import json
        params = {
            "aggression": self.aggression,
            "caution": self.caution,
            "team_focus": self.team_focus
        }
        with open(path, 'w') as f:
            json.dump(params, f)

    def load(self, path: str) -> None:
        """Parametreleri yükle."""
        import json
        with open(path, 'r') as f:
            params = json.load(f)
        self.aggression = params.get("aggression", 0.5)
        self.caution = params.get("caution", 0.5)
        self.team_focus = params.get("team_focus", 0.5)
