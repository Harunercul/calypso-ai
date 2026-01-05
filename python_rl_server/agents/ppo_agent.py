"""
PPO Agent - Proximal Policy Optimization
TÜBİTAK İP-2 AI Bot System

Referanslar:
- Chelarescu (2022): PPO for GVGAI
- Oh et al. (2022): Pro-level AI with self-play
- Schulman et al. (2017): Original PPO paper
"""

import os
from typing import Any, Dict, Optional, Tuple
import numpy as np
import torch

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv

from .base_agent import BaseAgent


class PPOAgent(BaseAgent):
    """
    PPO (Proximal Policy Optimization) Agent.

    Stable-Baselines3 kullanarak PPO implementasyonu.
    Hyperparametreler Chelarescu (2022) referans alınarak ayarlandı.
    """

    def __init__(
        self,
        name: str = "PPOAgent",
        observation_dim: int = 64,
        action_dim: int = 9,
        learning_rate: float = 3e-4,
        n_steps: int = 2048,
        batch_size: int = 64,
        n_epochs: int = 10,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_range: float = 0.2,
        ent_coef: float = 0.01,
        vf_coef: float = 0.5,
        max_grad_norm: float = 0.5,
        device: str = "auto",
        policy_kwargs: Optional[Dict] = None,
        verbose: int = 1
    ):
        """
        Args:
            name: Agent ismi
            observation_dim: Observation boyutu (default: 64)
            action_dim: Aksiyon sayısı (default: 9)
            learning_rate: Öğrenme hızı
            n_steps: Her update için step sayısı
            batch_size: Mini-batch boyutu
            n_epochs: Her update'te epoch sayısı
            gamma: Discount factor
            gae_lambda: GAE lambda
            clip_range: PPO clip range
            ent_coef: Entropy coefficient
            vf_coef: Value function coefficient
            max_grad_norm: Gradient clipping
            device: "auto", "cpu", veya "cuda"
            policy_kwargs: Policy network ayarları
            verbose: Log seviyesi
        """
        super().__init__(name, observation_dim, action_dim)

        self.learning_rate = learning_rate
        self.n_steps = n_steps
        self.batch_size = batch_size
        self.n_epochs = n_epochs
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_range = clip_range
        self.ent_coef = ent_coef
        self.vf_coef = vf_coef
        self.max_grad_norm = max_grad_norm
        self.device = device
        self.verbose = verbose

        # Default policy architecture
        if policy_kwargs is None:
            policy_kwargs = {
                "net_arch": dict(pi=[256, 256], vf=[256, 256]),
                "activation_fn": torch.nn.Tanh,
                "ortho_init": True
            }
        self.policy_kwargs = policy_kwargs

        # Model henüz oluşturulmadı
        self.model: Optional[PPO] = None
        self._env = None

        # Inference için buffer
        self._obs_buffer = None

    def initialize(self, env) -> None:
        """
        Environment ile model'i initialize et.

        Args:
            env: Gymnasium environment
        """
        self._env = env

        self.model = PPO(
            policy="MlpPolicy",
            env=env,
            learning_rate=self.learning_rate,
            n_steps=self.n_steps,
            batch_size=self.batch_size,
            n_epochs=self.n_epochs,
            gamma=self.gamma,
            gae_lambda=self.gae_lambda,
            clip_range=self.clip_range,
            ent_coef=self.ent_coef,
            vf_coef=self.vf_coef,
            max_grad_norm=self.max_grad_norm,
            policy_kwargs=self.policy_kwargs,
            device=self.device,
            verbose=self.verbose,
            tensorboard_log="./logs/tensorboard/"
        )

        print(f"[{self.name}] Model initialized on device: {self.model.device}")

    def select_action(
        self,
        observation: np.ndarray,
        deterministic: bool = False
    ) -> Tuple[int, Dict[str, float]]:
        """
        Observation'a göre aksiyon seç.

        Args:
            observation: 64-dim normalized observation
            deterministic: True = exploitation, False = exploration

        Returns:
            action: Seçilen aksiyon (0-8)
            info: Action probabilities ve değer tahmini
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        # Observation'ı doğru shape'e getir
        if observation.ndim == 1:
            observation = observation.reshape(1, -1)

        # Aksiyon seç
        action, _states = self.model.predict(
            observation,
            deterministic=deterministic
        )

        # Action probabilities ve value için
        info = {}

        with torch.no_grad():
            obs_tensor = torch.as_tensor(observation).float().to(self.model.device)

            # Policy'den distribution al
            distribution = self.model.policy.get_distribution(obs_tensor)
            probs = distribution.distribution.probs.cpu().numpy()[0]

            # Value tahmini
            value = self.model.policy.predict_values(obs_tensor).cpu().numpy().flatten()[0]

            # Info dict'e ekle
            for i, p in enumerate(probs):
                info[f"prob_{self.get_action_name(i)}"] = float(p)
            info["value_estimate"] = float(value.item()) if hasattr(value, 'item') else float(value)

        self.step()

        return int(action[0]) if isinstance(action, np.ndarray) else int(action), info

    def update(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool
    ) -> Dict[str, float]:
        """
        Single-step update (SB3 kendi buffer'ını yönetiyor).

        Not: SB3'te update otomatik yapılır, bu method manuel kontrol için.
        """
        # SB3 kendi rollout buffer'ını kullanıyor
        # Bu method daha çok debugging/logging için
        return {
            "reward": reward,
            "done": float(done)
        }

    def train(
        self,
        total_timesteps: int,
        callback: Optional[BaseCallback] = None,
        log_interval: int = 1,
        reset_num_timesteps: bool = True
    ) -> None:
        """
        Agent'ı eğit.

        Args:
            total_timesteps: Toplam training step sayısı
            callback: Training callback'leri
            log_interval: Log aralığı
            reset_num_timesteps: Timestep sayacını sıfırla
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        self.set_training_mode(True)

        print(f"[{self.name}] Starting training for {total_timesteps} timesteps...")

        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            log_interval=log_interval,
            reset_num_timesteps=reset_num_timesteps,
            progress_bar=True
        )

        self.set_training_mode(False)
        print(f"[{self.name}] Training completed!")

    def save(self, path: str) -> None:
        """
        Model'i kaydet.

        Args:
            path: Kayıt yolu (.zip uzantısı otomatik eklenir)
        """
        if self.model is None:
            raise RuntimeError("Model not initialized.")

        # Dizin yoksa oluştur
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

        self.model.save(path)
        print(f"[{self.name}] Model saved to: {path}")

    def load(self, path: str, env=None) -> None:
        """
        Model'i yükle.

        Args:
            path: Model dosyası yolu
            env: Opsiyonel environment (inference için gerekli değil)
        """
        if env is not None:
            self._env = env

        self.model = PPO.load(
            path,
            env=self._env,
            device=self.device
        )
        print(f"[{self.name}] Model loaded from: {path}")

    def get_training_metrics(self) -> Dict[str, float]:
        """Son training metriklerini döndür."""
        if self.model is None:
            return {}

        # Logger'dan metrikleri al
        metrics = {}
        if hasattr(self.model, 'logger') and self.model.logger is not None:
            # SB3 logger'dan metrikleri çek
            pass

        return metrics


class PPOTrainingCallback(BaseCallback):
    """
    PPO Training için custom callback.
    Checkpoint kaydetme, early stopping, vs.
    """

    def __init__(
        self,
        save_freq: int = 10000,
        save_path: str = "./models/checkpoints/",
        name_prefix: str = "ppo_checkpoint",
        verbose: int = 1
    ):
        super().__init__(verbose)
        self.save_freq = save_freq
        self.save_path = save_path
        self.name_prefix = name_prefix

        os.makedirs(save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.save_freq == 0:
            path = os.path.join(
                self.save_path,
                f"{self.name_prefix}_{self.n_calls}_steps"
            )
            self.model.save(path)
            if self.verbose > 0:
                print(f"[Callback] Checkpoint saved: {path}")
        return True

    def _on_training_end(self) -> None:
        # Final model kaydet
        path = os.path.join(self.save_path, f"{self.name_prefix}_final")
        self.model.save(path)
        if self.verbose > 0:
            print(f"[Callback] Final model saved: {path}")
