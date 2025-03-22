from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler
from rich import box
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime


class KradleLogger:
    def __init__(self):
        self.console = Console()
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging with Rich handler for beautiful formatting"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True, markup=True, show_time=False)],
        )
        # Keep Flask debug logs clean
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.handlers = []
        werkzeug_handler = logging.StreamHandler(sys.stdout)
        werkzeug_handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(message)s", "%H:%M:%S")
        )
        werkzeug_logger.addHandler(werkzeug_handler)
        werkzeug_logger.setLevel(logging.INFO)

    def display_startup_banner(self, config: Dict[str, Any]):
        """Display a beautiful startup banner with server information"""
        # self.console.clear()

        # Network URLs panel
        self.log_success(f"✨ {config.get('agent_username')} is running!\n\n")
        self.log_info(f" Agent is reachable at {config.get('agent_url')}\n\n")

        # Control tip
        self.console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")
        print()

    def log_success(self, message: str):
        """Log a success message"""
        self.console.print(f"✓ {message}", style="green")

    def log_error(self, message: str, error: Optional[Exception] = None):
        """Log an error message with optional exception details"""
        self.console.print(f"✕ {message}", style="red")
        if error:
            self.console.print(
                f"  → {type(error).__name__}: {str(error)}", style="red dim"
            )

    def log_warning(self, message: str):
        """Log a warning message"""
        self.console.print(f"! {message}", style="yellow")

    def log_info(self, message: str):
        """Log an informational message"""
        self.console.print(f"○ {message}", style="blue")

    def log_debug(self, message: str):
        """Log a debug message"""
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            self.console.print(f"· {message}", style="dim")

    def log_api_call(self, method: str, endpoint: str, status: int):
        """Log an API call with color-coded status"""
        status_color = "green" if 200 <= status < 300 else "red"
        method_width = 6  # Consistent width for method
        self.console.print(
            f"  {method:<{method_width}} {endpoint} [{status_color}]{status}[/]",
            style="dim",
        )

    def on_shutdown(self):
        """Display shutdown message"""
        self.console.print("\n[yellow]Shutting down Kradle Agent Server...[/yellow]")
