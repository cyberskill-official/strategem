"""Run API: python -m tamthuc_api"""

from __future__ import annotations

import os


def main() -> None:
    try:
        import uvicorn
    except ImportError as e:  # pragma: no cover
        raise SystemExit(
            "uvicorn is required to run the API. Install with: uv add uvicorn"
        ) from e
    from tamthuc_api.app import create_app

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(create_app(), host=host, port=port, reload=False)


if __name__ == "__main__":
    main()

