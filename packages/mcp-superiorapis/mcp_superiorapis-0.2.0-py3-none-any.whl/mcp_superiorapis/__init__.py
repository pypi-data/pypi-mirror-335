from . import server
import asyncio

def main():
    """Main entry point for the package."""
    try:
        loop = asyncio.get_running_loop()
        loop.run_until_complete(server.main())
    except RuntimeError:
        asyncio.run(server.main())

__all__ = ['main', 'server']