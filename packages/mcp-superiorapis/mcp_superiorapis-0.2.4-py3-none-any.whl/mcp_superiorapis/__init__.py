from . import server
import asyncio

def main():
    """Main entry point for the package."""
    try:
        asyncio.run(server.run_server())
    except Exception as e:
        import sys
        print(f"❌ Error in main program execution: {str(e)}", file=sys.stderr)

__all__ = ['main', 'server']