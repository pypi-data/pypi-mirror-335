import json
from pathlib import Path

import awesome_list_generator as alg


def main() -> None:
    with Path("docs/schema/config.json").open("w") as fp:
        json.dump(alg.config.Config.model_json_schema(), fp)


if __name__ == "__main__":
    main()
