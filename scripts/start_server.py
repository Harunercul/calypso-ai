#!/usr/bin/env python3
"""
Server Start Script
TÜBİTAK İP-2 AI Bot System

gRPC server'ı başlatmak için script.

Usage:
    python scripts/start_server.py --port 50051
    python scripts/start_server.py --model ./models/ppo_best.zip --port 50051
    python scripts/start_server.py --rule-based --port 50051
"""

import argparse
import os
import sys
import signal

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python_rl_server.server import BotAIServer
from python_rl_server.agents import PPOAgent, RuleBasedAgent
from python_rl_server.utils import setup_logger


def parse_args():
    parser = argparse.ArgumentParser(description="Start Bot AI gRPC Server")

    parser.add_argument(
        "--host", type=str, default="0.0.0.0",
        help="Server host"
    )
    parser.add_argument(
        "--port", type=int, default=50051,
        help="Server port"
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help="Path to trained PPO model"
    )
    parser.add_argument(
        "--rule-based", action="store_true",
        help="Use rule-based agent instead of PPO"
    )
    parser.add_argument(
        "--workers", type=int, default=10,
        help="Number of worker threads"
    )
    parser.add_argument(
        "--log-file", type=str, default="./logs/server.log",
        help="Log file path"
    )
    parser.add_argument(
        "--verbose", type=int, default=1,
        help="Verbosity level"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Logger setup
    logger = setup_logger(
        name="bot_ai_server",
        log_file=args.log_file
    )

    print(f"=" * 60)
    print(f"TÜBİTAK İP-2 Bot AI Server")
    print(f"=" * 60)

    # Agent oluştur
    if args.rule_based:
        print("Using Rule-Based Agent")
        agent = RuleBasedAgent(
            aggression=0.5,
            caution=0.5,
            team_focus=0.5
        )
    else:
        print("Using PPO Agent")
        agent = PPOAgent(verbose=args.verbose)

        if args.model and os.path.exists(args.model):
            print(f"Loading model from: {args.model}")
            # PPO için environment gerekli, mock env kullan
            from python_rl_server.environments import MockCombatEnv
            mock_env = MockCombatEnv()
            agent.initialize(mock_env)
            agent.load(args.model)
            mock_env.close()
        else:
            print("WARNING: No model specified. Agent will use random actions.")
            print("Train a model first or use --rule-based flag.")

    # Server oluştur
    server = BotAIServer(
        agent=agent,
        host=args.host,
        port=args.port,
        max_workers=args.workers
    )

    # Graceful shutdown handler
    def signal_handler(sig, frame):
        print("\nShutting down server...")
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"\nServer configuration:")
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  Workers: {args.workers}")
    print(f"  Agent: {'Rule-Based' if args.rule_based else 'PPO'}")
    print(f"\nStarting server...")
    print(f"Press Ctrl+C to stop")
    print("-" * 60)

    # Server başlat
    server.start(blocking=True)


if __name__ == "__main__":
    main()
