"""
gRPC Server Implementation
TÜBİTAK İP-2 AI Bot System

Unreal Engine ile iletişim için gRPC server.
"""

import os
import sys
import time
from concurrent import futures
from typing import Dict, Optional
import threading

import grpc
import numpy as np

# Proto generated files (proto compile edildikten sonra import edilecek)
# from . import bot_service_pb2
# from . import bot_service_pb2_grpc

from ..agents import PPOAgent, RuleBasedAgent, BaseAgent
from ..difficulty import DifficultyManager
from ..environments import ObservationBuilder


class BotAIServicer:
    """
    BotAIService gRPC implementasyonu.

    Not: Proto dosyaları compile edilmeden önce bu class
    bot_service_pb2_grpc.BotAIServiceServicer'ı inherit etmeli.
    """

    def __init__(
        self,
        agent: BaseAgent,
        difficulty_manager: Optional[DifficultyManager] = None
    ):
        """
        Args:
            agent: RL veya Rule-based agent
            difficulty_manager: Opsiyonel DDA manager
        """
        self.agent = agent
        self.difficulty_manager = difficulty_manager or DifficultyManager()
        self._obs_builder = ObservationBuilder()

        # Stats
        self._request_count = 0
        self._total_inference_time = 0.0

    def GetAction(self, request, context):
        """
        Tek bot için aksiyon döndür.

        Proto compile edildikten sonra aktif olacak.
        """
        start_time = time.time()
        self._request_count += 1

        # GameState'i observation array'e çevir
        observation = self._game_state_to_observation(request)

        # Agent'tan aksiyon al
        deterministic = not self.agent.is_training
        action, info = self.agent.select_action(observation, deterministic=deterministic)

        # Response oluştur (proto compile edildikten sonra)
        # response = bot_service_pb2.BotAction(
        #     bot_id=request.bot_id,
        #     timestamp=int(time.time() * 1000),
        #     action_type=action,
        #     confidence=info.get("value_estimate", 0.0)
        # )

        self._total_inference_time += time.time() - start_time

        # Şimdilik dict döndür
        return {
            "bot_id": getattr(request, 'bot_id', 'test'),
            "action_type": action,
            "action_name": self.agent.get_action_name(action),
            "confidence": info.get("value_estimate", 0.0),
            "utility_scores": {k: v for k, v in info.items() if k.startswith("prob_") or k.startswith("utility_")}
        }

    def GetActionsBatch(self, request, context):
        """Batch aksiyon - birden fazla bot."""
        actions = []
        for state in request.states:
            action = self.GetAction(state, context)
            actions.append(action)
        return {"actions": actions}

    def SendReward(self, request, context):
        """Reward sinyali al (training mode)."""
        # Training mode'da reward'ı agent'a ilet
        return {"success": True, "message": "Reward received"}

    def EndEpisode(self, request, context):
        """Episode sonu."""
        self.agent.reset()
        return {"success": True, "message": "Episode ended"}

    def _game_state_to_observation(self, game_state) -> np.ndarray:
        """GameState proto'yu 64-dim observation'a çevir."""
        # Proto compile edilince gerçek dönüşüm yapılacak
        # Şimdilik mock
        if hasattr(game_state, 'self_state'):
            # Gerçek proto
            pass
        else:
            # Mock/test için random observation
            return np.random.rand(64).astype(np.float32)

        return self._obs_builder.build()

    def get_stats(self) -> Dict:
        """Server istatistikleri."""
        avg_time = (self._total_inference_time / self._request_count
                    if self._request_count > 0 else 0)
        return {
            "request_count": self._request_count,
            "avg_inference_time_ms": avg_time * 1000,
            "total_inference_time_s": self._total_inference_time
        }


class TrainingServicer:
    """Training servisi implementasyonu."""

    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self._is_training = False
        self._training_thread: Optional[threading.Thread] = None

    def StartTraining(self, request, context):
        """Training başlat."""
        if self._is_training:
            return {"is_training": True, "status_message": "Already training"}

        self._is_training = True
        # Training thread başlat (async)
        return {
            "is_training": True,
            "status_message": "Training started",
            "total_timesteps": getattr(request, 'total_timesteps', 100000)
        }

    def StopTraining(self, request, context):
        """Training durdur."""
        self._is_training = False
        return {"is_training": False, "status_message": "Training stopped"}

    def GetTrainingStatus(self, request, context):
        """Training durumu."""
        return {
            "is_training": self._is_training,
            "status_message": "Training" if self._is_training else "Idle"
        }

    def SaveModel(self, request, context):
        """Model kaydet."""
        try:
            path = getattr(request, 'path', './models/saved_model')
            self.agent.save(path)
            return {"success": True, "message": f"Model saved to {path}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def LoadModel(self, request, context):
        """Model yükle."""
        try:
            path = getattr(request, 'path', './models/saved_model')
            self.agent.load(path)
            return {"success": True, "message": f"Model loaded from {path}"}
        except Exception as e:
            return {"success": False, "message": str(e)}


class DifficultyServicer:
    """Difficulty servisi implementasyonu."""

    def __init__(self, difficulty_manager: DifficultyManager):
        self.manager = difficulty_manager

    def UpdatePlayerMetrics(self, request, context):
        """Oyuncu metriklerini güncelle."""
        player_id = getattr(request, 'player_id', 'default')

        tracker = self.manager.get_tracker(player_id)

        # Metrikleri kaydet
        if hasattr(request, 'recent_kills'):
            for _ in range(request.recent_kills):
                tracker.record_kill()

        if hasattr(request, 'recent_deaths'):
            for _ in range(request.recent_deaths):
                tracker.record_death()

        # Zorluk güncelle
        self.manager.update_difficulty(player_id)

        return self.manager.get_difficulty_info(player_id)

    def GetCurrentDifficulty(self, request, context):
        """Mevcut zorluk."""
        player_id = getattr(request, 'player_id', 'default')
        return self.manager.get_difficulty_info(player_id)

    def SetDifficulty(self, request, context):
        """Manuel zorluk ayarla."""
        player_id = getattr(request, 'player_id', 'default')
        level = getattr(request, 'difficulty_level', 3)
        self.manager.set_difficulty(player_id, level)
        return {"success": True, "message": f"Difficulty set to {level}"}


class HealthServicer:
    """Health check servisi."""

    def __init__(self):
        self._start_time = time.time()
        self._version = "0.1.0"

    def Check(self, request, context):
        """Health check."""
        return {
            "status": "SERVING",
            "version": self._version,
            "uptime_seconds": int(time.time() - self._start_time)
        }


class BotAIServer:
    """
    Ana gRPC Server class'ı.

    Tüm servisleri bir arada yönetir.
    """

    def __init__(
        self,
        agent: Optional[BaseAgent] = None,
        host: str = "0.0.0.0",
        port: int = 50051,
        max_workers: int = 10
    ):
        """
        Args:
            agent: RL agent (None ise default oluşturulur)
            host: Server host
            port: Server port
            max_workers: Thread pool size
        """
        self.host = host
        self.port = port
        self.max_workers = max_workers

        # Agent
        self.agent = agent or RuleBasedAgent()

        # Managers
        self.difficulty_manager = DifficultyManager()

        # Servicers
        self.bot_servicer = BotAIServicer(self.agent, self.difficulty_manager)
        self.training_servicer = TrainingServicer(self.agent)
        self.difficulty_servicer = DifficultyServicer(self.difficulty_manager)
        self.health_servicer = HealthServicer()

        # gRPC server
        self._server: Optional[grpc.Server] = None
        self._is_running = False

    def start(self, blocking: bool = True) -> None:
        """
        Server'ı başlat.

        Args:
            blocking: True ise block eder, False ise background'da çalışır
        """
        self._server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self.max_workers)
        )

        # Servisleri ekle
        # Proto compile edildikten sonra:
        # bot_service_pb2_grpc.add_BotAIServiceServicer_to_server(
        #     self.bot_servicer, self._server
        # )
        # ...

        address = f"{self.host}:{self.port}"
        self._server.add_insecure_port(address)

        print(f"[BotAIServer] Starting server on {address}...")
        self._server.start()
        self._is_running = True
        print(f"[BotAIServer] Server started!")

        if blocking:
            try:
                self._server.wait_for_termination()
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """Server'ı durdur."""
        if self._server:
            print("[BotAIServer] Stopping server...")
            self._server.stop(grace=5)
            self._is_running = False
            print("[BotAIServer] Server stopped.")

    def is_running(self) -> bool:
        """Server çalışıyor mu?"""
        return self._is_running

    def get_stats(self) -> Dict:
        """Server istatistikleri."""
        return {
            "server": {
                "host": self.host,
                "port": self.port,
                "is_running": self._is_running
            },
            "inference": self.bot_servicer.get_stats(),
            "health": self.health_servicer.Check(None, None)
        }


def serve(
    model_path: Optional[str] = None,
    host: str = "0.0.0.0",
    port: int = 50051,
    use_rule_based: bool = False
) -> BotAIServer:
    """
    Server'ı başlat (convenience function).

    Args:
        model_path: Yüklenecek model yolu (None = yeni model)
        host: Server host
        port: Server port
        use_rule_based: True ise rule-based agent kullan

    Returns:
        BotAIServer instance
    """
    # Agent oluştur
    if use_rule_based:
        agent = RuleBasedAgent()
        print("[serve] Using Rule-Based Agent")
    else:
        agent = PPOAgent()
        if model_path and os.path.exists(model_path):
            agent.load(model_path)
            print(f"[serve] Loaded PPO model from {model_path}")
        else:
            print("[serve] Using new PPO Agent (not trained)")

    # Server oluştur ve başlat
    server = BotAIServer(agent=agent, host=host, port=port)
    return server


if __name__ == "__main__":
    # Direct execution için
    server = serve(use_rule_based=True)
    server.start(blocking=True)
