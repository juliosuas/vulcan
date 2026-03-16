"""Configuration management for Vulcan."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass
class Config:
    """Central configuration loaded from env vars and optional YAML config file."""

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "claude"

    # Scan
    scan_mode: str = "standard"
    target: str = ""

    # Execution
    cmd_timeout: int = 300
    max_concurrency: int = 5

    # Output
    output_dir: str = "./vulcan_output"
    report_format: str = "html"

    # Tool paths (auto-detected or overridden)
    tool_paths: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, config_path: str | None = None, env_file: str | None = None) -> Config:
        """Load configuration from env vars, .env file, and optional YAML config."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        cfg = cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            llm_provider=os.getenv("VULCAN_LLM_PROVIDER", "claude"),
            scan_mode=os.getenv("VULCAN_SCAN_MODE", "standard"),
            cmd_timeout=int(os.getenv("VULCAN_CMD_TIMEOUT", "300")),
            max_concurrency=int(os.getenv("VULCAN_MAX_CONCURRENCY", "5")),
            output_dir=os.getenv("VULCAN_OUTPUT_DIR", "./vulcan_output"),
            report_format=os.getenv("VULCAN_REPORT_FORMAT", "html"),
        )

        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}
            for key, value in data.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, value)

        return cfg

    def ensure_output_dir(self) -> Path:
        """Create and return the output directory."""
        p = Path(self.output_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_api_key(self) -> str:
        """Return the API key for the configured LLM provider."""
        if self.llm_provider == "claude":
            return self.anthropic_api_key
        return self.openai_api_key
