"""Generate the committed OpenAPI document from the application."""

import json
from pathlib import Path

from roster_balance.main import app


def main() -> None:
    output_path = Path(__file__).parents[2] / 'docs' / 'openapi.json'
    output_path.write_text(
        json.dumps(app.openapi(), indent=2) + '\n',
        encoding='utf-8',
    )


if __name__ == '__main__':
    main()
