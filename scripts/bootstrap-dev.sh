#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v brew >/dev/null 2>&1; then
  echo "[bootstrap] Homebrew not found. Install Homebrew first." >&2
  exit 1
fi

echo "[bootstrap] installing system dependencies from Brewfile..."
brew bundle --file "${ROOT_DIR}/Brewfile"

if ! command -v rustup >/dev/null 2>&1; then
  echo "[bootstrap] rustup not found after brew bundle; install rust toolchain manually." >&2
  exit 1
fi

echo "[bootstrap] ensuring Rust toolchain..."
rustup show active-toolchain >/dev/null 2>&1 || rustup default stable

echo "[bootstrap] fetching Rust dependencies..."
cargo fetch --manifest-path "${ROOT_DIR}/codex-rs/Cargo.toml"

echo "[bootstrap] linking helios dev binaries..."
"${ROOT_DIR}/scripts/install-helios-dev.sh"

echo "[bootstrap] done."
