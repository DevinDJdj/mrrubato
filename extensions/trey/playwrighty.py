#library to manage web interaction.  
#>pip install playwright
#>playwright install
#>pip install asyncio
import asyncio
from playwright.async_api import async_playwright

#standard libraries
import logging
import os
import time
import sys
import threading
import psutil


#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
import config 

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(filename='trey.log', 
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    async with async_playwright() as p:
        for browser_type in [p.chromium, p.firefox, p.webkit]:
            browser = await browser_type.launch()
            page = await browser.new_page()
            await page.goto('http://playwright.dev')
            await page.screenshot(path=f'example-{browser_type.name}.png')
            await browser.close()


    
if __name__ == "__main__":
    asyncio.run(main())
    #main()
