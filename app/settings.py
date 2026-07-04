from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parents[1]
    data_dir: Path = project_root / "data"
    database_path: Path = data_dir / "sgodai.sqlite"
    config_dir: Path = project_root / "configs"
    disclaimer: str = (
        "This system does not constitute investment advice, does not execute trades, "
        "and does not provide deterministic buy or sell instructions."
    )


settings = Settings()

