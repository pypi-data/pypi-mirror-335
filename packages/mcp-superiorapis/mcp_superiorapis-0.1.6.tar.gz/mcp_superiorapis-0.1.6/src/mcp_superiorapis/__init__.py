from . import server

async def main():
    """Main entry point for the package."""
    await server.main()

# Optionally expose other important items at package level
__all__ = ['main', 'server']