from simplex import Simplex
import os
from dotenv import load_dotenv
import time
from playwright.async_api import Page

import asyncio
import os
import dotenv

dotenv.load_dotenv()

async def main():
    simplex = Simplex(os.getenv("SIMPLEX_API_KEY"))

    simplex.create_session()
    simplex.goto("https://gmail.com")
    simplex.type("test@gmail.com")
    simplex.press_enter()
    simplex.wait(1000000)
if __name__ == "__main__":
    asyncio.run(main())
    