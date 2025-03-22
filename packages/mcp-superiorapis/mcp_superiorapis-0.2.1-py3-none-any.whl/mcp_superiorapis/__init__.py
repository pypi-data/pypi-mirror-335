from . import server


def main():
    """Main entry point for the package."""
    import asyncio
    asyncio.run(server.main())
    server.mcp.run()

__all__ = ['main', 'server']