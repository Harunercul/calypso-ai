"""
Logging Utilities
TÜBİTAK İP-2 AI Bot System
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


_loggers: dict = {}


def setup_logger(
    name: str = "calypso_ai",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Logger oluştur ve yapılandır.

    Args:
        name: Logger ismi
        level: Log seviyesi
        log_file: Opsiyonel log dosyası
        console: Console'a yaz?
        format_string: Custom format

    Returns:
        Configured logger
    """
    global _loggers

    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = []  # Clear existing handlers

    # Format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger


def get_logger(name: str = "calypso_ai") -> logging.Logger:
    """
    Mevcut logger'ı al veya yenisini oluştur.
    """
    if name in _loggers:
        return _loggers[name]
    return setup_logger(name)


class TrainingLogger:
    """Training için özel logger."""

    def __init__(
        self,
        log_dir: str = "./logs",
        experiment_name: Optional[str] = None
    ):
        """
        Args:
            log_dir: Log dizini
            experiment_name: Experiment ismi (None = timestamp)
        """
        if experiment_name is None:
            experiment_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.log_dir = os.path.join(log_dir, experiment_name)
        os.makedirs(self.log_dir, exist_ok=True)

        self.logger = setup_logger(
            name=f"training_{experiment_name}",
            log_file=os.path.join(self.log_dir, "training.log")
        )

        self._metrics_file = os.path.join(self.log_dir, "metrics.csv")
        self._metrics_initialized = False

    def log(self, message: str, level: int = logging.INFO) -> None:
        """Log mesajı."""
        self.logger.log(level, message)

    def log_metrics(self, step: int, metrics: dict) -> None:
        """Metrikleri CSV'ye yaz."""
        import csv

        # İlk çağrıda header yaz
        if not self._metrics_initialized:
            with open(self._metrics_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['step'] + list(metrics.keys()))
            self._metrics_initialized = True

        # Metrikleri yaz
        with open(self._metrics_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([step] + list(metrics.values()))

    def log_hyperparams(self, params: dict) -> None:
        """Hyperparametreleri kaydet."""
        import json
        path = os.path.join(self.log_dir, "hyperparams.json")
        with open(path, 'w') as f:
            json.dump(params, f, indent=2)

    def get_log_dir(self) -> str:
        """Log dizinini döndür."""
        return self.log_dir
