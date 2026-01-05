"""
Training Callbacks
TÜBİTAK İP-2 AI Bot System

Custom callbacks for training monitoring and checkpointing.
"""

import os
from typing import Dict, Optional, Any
import numpy as np

from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.logger import TensorBoardOutputFormat


class TrainingCallback(BaseCallback):
    """
    Ana training callback.

    - Checkpoint kaydetme
    - Custom metrikleri logging
    - Early stopping (opsiyonel)
    """

    def __init__(
        self,
        save_freq: int = 10000,
        save_path: str = "./models/checkpoints/",
        name_prefix: str = "ppo_bot",
        log_freq: int = 1000,
        early_stop_reward: Optional[float] = None,
        early_stop_patience: int = 10,
        verbose: int = 1
    ):
        """
        Args:
            save_freq: Kaç step'te bir checkpoint kaydet
            save_path: Checkpoint dizini
            name_prefix: Model isim prefix'i
            log_freq: Kaç step'te bir log yaz
            early_stop_reward: Bu reward'a ulaşınca dur (None = devre dışı)
            early_stop_patience: Kaç eval'de gelişme olmazsa dur
            verbose: Log seviyesi
        """
        super().__init__(verbose)

        self.save_freq = save_freq
        self.save_path = save_path
        self.name_prefix = name_prefix
        self.log_freq = log_freq
        self.early_stop_reward = early_stop_reward
        self.early_stop_patience = early_stop_patience

        self.best_mean_reward = -np.inf
        self.no_improvement_count = 0

        os.makedirs(save_path, exist_ok=True)

    def _init_callback(self) -> None:
        """Callback initialization."""
        if self.verbose > 0:
            print(f"[TrainingCallback] Initialized. Save path: {self.save_path}")

    def _on_step(self) -> bool:
        """Her step'te çağrılır."""

        # Checkpoint kaydetme
        if self.n_calls % self.save_freq == 0:
            path = os.path.join(
                self.save_path,
                f"{self.name_prefix}_{self.n_calls}_steps"
            )
            self.model.save(path)
            if self.verbose > 0:
                print(f"[Checkpoint] Saved: {path}")

        # Custom logging
        if self.n_calls % self.log_freq == 0:
            self._log_custom_metrics()

        return True

    def _log_custom_metrics(self) -> None:
        """Custom metrikleri tensorboard'a yaz."""
        # Episode info'dan metrikleri çek
        if len(self.model.ep_info_buffer) > 0:
            ep_rewards = [ep_info["r"] for ep_info in self.model.ep_info_buffer]
            ep_lengths = [ep_info["l"] for ep_info in self.model.ep_info_buffer]

            mean_reward = np.mean(ep_rewards)
            mean_length = np.mean(ep_lengths)

            self.logger.record("custom/mean_episode_reward", mean_reward)
            self.logger.record("custom/mean_episode_length", mean_length)
            self.logger.record("custom/total_steps", self.n_calls)

            # Best reward tracking
            if mean_reward > self.best_mean_reward:
                self.best_mean_reward = mean_reward
                self.no_improvement_count = 0

                # Best model kaydet
                best_path = os.path.join(self.save_path, f"{self.name_prefix}_best")
                self.model.save(best_path)
                if self.verbose > 0:
                    print(f"[Best Model] New best reward: {mean_reward:.2f}")
            else:
                self.no_improvement_count += 1

    def _on_training_end(self) -> None:
        """Training bitince çağrılır."""
        # Final model kaydet
        final_path = os.path.join(self.save_path, f"{self.name_prefix}_final")
        self.model.save(final_path)
        if self.verbose > 0:
            print(f"[TrainingCallback] Final model saved: {final_path}")
            print(f"[TrainingCallback] Best reward achieved: {self.best_mean_reward:.2f}")


class EvaluationCallback(BaseCallback):
    """
    Evaluation callback.

    Periyodik olarak agent'ı evaluate eder ve sonuçları loglar.
    """

    def __init__(
        self,
        eval_env,
        eval_freq: int = 10000,
        n_eval_episodes: int = 10,
        deterministic: bool = True,
        verbose: int = 1
    ):
        """
        Args:
            eval_env: Evaluation environment
            eval_freq: Kaç step'te bir evaluate et
            n_eval_episodes: Kaç episode evaluate et
            deterministic: Deterministic policy mi?
            verbose: Log seviyesi
        """
        super().__init__(verbose)

        self.eval_env = eval_env
        self.eval_freq = eval_freq
        self.n_eval_episodes = n_eval_episodes
        self.deterministic = deterministic

        self.eval_results = []

    def _on_step(self) -> bool:
        """Her step'te çağrılır."""
        if self.n_calls % self.eval_freq == 0:
            self._evaluate()
        return True

    def _evaluate(self) -> None:
        """Agent'ı evaluate et."""
        episode_rewards = []
        episode_lengths = []
        episode_infos = []

        for _ in range(self.n_eval_episodes):
            obs, info = self.eval_env.reset()
            done = False
            truncated = False
            episode_reward = 0.0
            episode_length = 0

            while not done and not truncated:
                action, _ = self.model.predict(obs, deterministic=self.deterministic)
                obs, reward, done, truncated, info = self.eval_env.step(action)
                episode_reward += reward
                episode_length += 1

            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            episode_infos.append(info)

        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)
        mean_length = np.mean(episode_lengths)

        # Log results
        self.logger.record("eval/mean_reward", mean_reward)
        self.logger.record("eval/std_reward", std_reward)
        self.logger.record("eval/mean_length", mean_length)

        # Custom info metrikleri
        if episode_infos:
            for key in episode_infos[0].keys():
                if isinstance(episode_infos[0][key], (int, float)):
                    values = [info[key] for info in episode_infos]
                    self.logger.record(f"eval/{key}", np.mean(values))

        self.eval_results.append({
            "step": self.n_calls,
            "mean_reward": mean_reward,
            "std_reward": std_reward,
            "mean_length": mean_length
        })

        if self.verbose > 0:
            print(f"[Eval] Step {self.n_calls}: "
                  f"Reward = {mean_reward:.2f} +/- {std_reward:.2f}, "
                  f"Length = {mean_length:.1f}")

    def get_results(self) -> list:
        """Tüm evaluation sonuçlarını döndür."""
        return self.eval_results


class CurriculumCallback(BaseCallback):
    """
    Curriculum Learning callback.

    Referans: Oh et al. (2022) - Pro-level AI training
    """

    def __init__(
        self,
        env,
        stages: list,
        verbose: int = 1
    ):
        """
        Args:
            env: Training environment (difficulty ayarlanabilir olmalı)
            stages: List of dicts with 'timesteps' and 'difficulty'
            verbose: Log seviyesi
        """
        super().__init__(verbose)

        self.env = env
        self.stages = stages
        self.current_stage = 0

    def _on_step(self) -> bool:
        """Stage geçişlerini kontrol et."""
        if self.current_stage < len(self.stages) - 1:
            next_stage = self.stages[self.current_stage + 1]

            if self.n_calls >= next_stage.get("timesteps", float("inf")):
                self.current_stage += 1
                new_difficulty = next_stage["difficulty"]

                # Environment difficulty'sini güncelle
                if hasattr(self.env, "difficulty"):
                    self.env.difficulty = new_difficulty / 7.0  # 1-7 -> 0-1 normalize

                if self.verbose > 0:
                    print(f"[Curriculum] Stage {self.current_stage}: "
                          f"Difficulty = {new_difficulty}")

                self.logger.record("curriculum/stage", self.current_stage)
                self.logger.record("curriculum/difficulty", new_difficulty)

        return True
