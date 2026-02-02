import json
import logging
from pathlib import Path


def load_rules(file="category_rules.json") -> dict[str, list[str]]:
    path = Path(file)
    default_rules = {"other": []}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                out: dict[str, list[str]] = {}
                for k, v in data.items():
                    k = str(k).strip()
                    if not k:
                        continue
                    if isinstance(v, list):
                        out[k] = [str(x) for x in v if str(x).strip()]
                    else:
                        out[k] = []
                return out
        except Exception as e:
            logging.exception(e)
    return default_rules.copy()


def persist(rules: dict[str, list[str]], file="category_rules.json", ) -> None:
    path = Path(file)
    try:
        path.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logging.exception(e)


def normalize_rules(rules: dict[str, list[str]]) -> dict[str, list[str]]:
    return {
        str(k).strip(): [str(x).strip() for x in v if str(x).strip()]
        for k, v in rules.items()
        if str(k).strip()
    }
