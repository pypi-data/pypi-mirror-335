"""
Shared console instance for CLI output.
"""
from rich.console import Console

# Create a singleton console instance
console = Console()

__all__ = ['console']