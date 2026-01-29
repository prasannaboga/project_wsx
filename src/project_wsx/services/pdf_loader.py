import yaml
from pathlib import Path


def load_documents(config_path: str):
    config = yaml.safe_load(Path(config_path).read_text())
    for year, months in config["documents"].items():
        for month, paths in months.items():
            for path in paths:
                yield {
                    "year": year,
                    "month": month,
                    "path": path,
                    "source": Path(path).name,
                }
