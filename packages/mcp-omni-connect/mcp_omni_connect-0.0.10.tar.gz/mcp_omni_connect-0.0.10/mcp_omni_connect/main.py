import asyncio
import signal
import sys
import os
from pathlib import Path
import shutil
from mcp_omni_connect.client import MCPClient, Configuration
from mcp_omni_connect.cli import MCPClientCLI
from mcp_omni_connect.utils import logger

DEFAULT_CONFIG_NAME = "servers_config.json"

def get_default_config_path():
    """Get the path to the default config file in the package"""
    return os.path.join(os.path.dirname(__file__), "config", DEFAULT_CONFIG_NAME)

def ensure_config_exists():
    """Ensure config file exists in user's directory or create from default"""
    user_config = Path.cwd() / DEFAULT_CONFIG_NAME
    if not user_config.exists():
        default_config = Path(get_default_config_path())
        if default_config.exists():
            shutil.copy(default_config, user_config)
            logger.info(f"Created default configuration file at: {user_config}")
        else:
            logger.error("Default configuration file not found in package!")
            sys.exit(1)
    return user_config

async def cleanup_handler(client):
    """Handle cleanup with a timeout"""
    try:
        async with asyncio.timeout(3.0):
            await client.cleanup()
    except asyncio.TimeoutError:
        logger.warning("Cleanup timed out, forcing exit")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    finally:
        # Cancel all remaining tasks except the current one
        current_task = asyncio.current_task()
        for task in asyncio.all_tasks():
            if task is not current_task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error cancelling task: {e}")

async def async_main():
    """Async main function"""
    client = None
    try:
        # Ensure config exists
        config_path = ensure_config_exists()
        
        # Initialize client
        config = Configuration()
        client = MCPClient(config)
        cli = MCPClientCLI(client)
        
        # Set up signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(cleanup_handler(client)))
        
        # Connect and start chat loop
        await client.connect_to_servers()
        await cli.chat_loop()
        
    except KeyboardInterrupt:
        logger.info("Shutting down client...")
        if client:
            await cleanup_handler(client)
    except Exception as e:
        logger.error(f"Error: {e}")
        if client:
            await cleanup_handler(client)
    finally:
        # Remove signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.remove_signal_handler(sig)
            except Exception as e:
                logger.error(f"Error removing signal handler: {e}")

def main():
    """Main entry point for the CLI"""
    try:
        if sys.platform.startswith('win'):
            # Set up proper signal handling on Windows
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        asyncio.run(async_main())
        
    except KeyboardInterrupt:
        pass  # Clean exit on Ctrl+C
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()