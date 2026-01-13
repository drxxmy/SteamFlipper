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

    # Configure project loggers
    logging.getLogger("steamflipper.market").setLevel(logging.DEBUG)

    # Silence noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
