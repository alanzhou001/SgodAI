import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path = field(
        default_factory=lambda: Path(os.getenv("SGODAI_PROJECT_ROOT", Path(__file__).resolve().parents[1]))
    )
    data_dir: Path = field(
        default_factory=lambda: Path(os.getenv("SGODAI_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
    )
    database_path: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "SGODAI_DB_PATH",
                Path(os.getenv("SGODAI_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
                / "sgodai.sqlite",
            )
        )
    )
    config_dir: Path = field(
        default_factory=lambda: Path(os.getenv("SGODAI_CONFIG_DIR", Path(__file__).resolve().parents[1] / "configs"))
    )
    disclaimer: str = (
        "This system does not constitute investment advice, does not execute trades, "
        "and does not provide deterministic buy or sell instructions."
    )


settings = Settings()
