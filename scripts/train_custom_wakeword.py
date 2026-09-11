# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Orchestration helper for training a custom openWakeWord model
# on the phrases "okay saphira", "hey saphira", "saphira".
# Because of 2026 dependency fragility, the recommended path remains
# a maintained Colab notebook or the Docker pipeline
# (briankelley/atlas-voice-training). This script documents the
# exact phrases and output location expected by Saphira.

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SaphiraWakeWordTrainer")

DEFAULT_PHRASES = ["okay saphira", "hey saphira", "saphira"]
DEFAULT_OUTPUT_DIR = Path("voice/models")


def main() -> int:
    parser = argparse.ArgumentParser(description="Saphira openWakeWord training orchestrator")
    parser.add_argument("--phrases", nargs="+", default=DEFAULT_PHRASES)
    parser.add_argument("--model-name", default="saphira")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--n-samples", type=int, default=15000)
    parser.add_argument("--steps", type=int, default=30000)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=== Saphira Custom Wake-Word Training ===")
    logger.info("Target phrases : %s", args.phrases)
    logger.info("Model name     : %s", args.model_name)
    logger.info("Output dir     : %s", args.output_dir.resolve())
    logger.info("Samples / steps: %d / %d", args.n_samples, args.steps)
    logger.info("")
    logger.info("RECOMMENDED PATH (2026):")
    logger.info("  1. Use a maintained Colab notebook (search 'openwakeword-colab-2026')")
    logger.info("     or the Docker pipeline: https://github.com/briankelley/atlas-voice-training")
    logger.info("  2. Set TARGET_PHRASE = %s", args.phrases)
    logger.info("  3. After training, copy the resulting .onnx (and .onnx.data if present)")
    logger.info("     into %s", args.output_dir.resolve())
    logger.info("  4. Export environment:")
    logger.info("       export SAPHIRA_OWW_MODEL_PATH=%s/%s.onnx", args.output_dir.resolve(), args.model_name)
    logger.info("       export SAPHIRA_WAKE_ENGINE=openwakeword")
    logger.info("       export SAPHIRA_WAKE_SENSITIVITY=0.45")
    logger.info("")
    logger.info("Saphira will load the custom model automatically via voice/wake_word.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
