from rich.console import Console

from vajra.logger import init_logger

logger = init_logger(__name__)
console: Console = Console(force_terminal=True)


def log_and_print_info(message: str):
    logger.info(message)
    console.print(message)


def log_and_print_warning(message: str):
    logger.warning(message)
    console.print(f"[yellow]{message}[/yellow]")


def log_and_print_error(message: str):
    logger.error(message)
    console.print(f"[red]{message}[/red]")
