import os
import importlib
from .config import client

async def start_bot():
    """Starts the userbot and loads necessary modules."""
    for file in os.listdir("UbLite"):
        if file.endswith(".py") and file not in ("__init__.py", "config.py", "setup_config.py"):
            module_name = f"UbLite.{file[:-3]}"
            importlib.import_module(module_name)

    print("UbLite Userbot is running...")
    await client.start()
    await client.run_until_disconnected()

def main():
    """Entry point for the script."""
    import asyncio
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\nUserbot stopped by user.")

if __name__ == "__main__":
    main()
