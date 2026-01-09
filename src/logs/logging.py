import logging

from rich.logging import RichHandler


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(name)s] %(message)s",
        handlers=[
            RichHandler(
                show_time=True,
                show_level=True,
                show_path=False,
                markup=True,
            )
        ],
    )

    # Silence noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
