#library to manage web interaction.  
#>pip install playwright
#>playwright install
#>pip install asyncio
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


from playwright.sync_api import sync_playwright


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

page_cache = [] # this should include history of pages each time.  
#array of arrays with {query, page, body, links, title, reader_queue, sim_queue, reader_stop_event}

mybrowser = None
myplaywright = None
mycontext = None

current_cache = -1 #current cache page we are on.

#text_offset is how far into the text we are.  link_offset is which link to click relative to that we want to click.
#usually this will be 0 or -1 to go back one link.
def click_link(cacheno, text_offset, link_offset=0, open_new_tab=False):

    global current_cache
    if (cacheno < 0):
        cacheno = current_cache

    if (text_offset < 0):
        text_offset = 0
    

    """Click a link on a cached page."""
    if cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        page = page_info['page']
        links = page_info['links']
        linkno = 0
        for i, link in enumerate(links):
            if 'offset' in link and link['offset'] <= text_offset:
                linkno = i
        if (link_offset != 0):
            linkno += link_offset
        if linkno < len(links) and linkno >= 0:
            link = links[linkno]
            href = link['href']
            if href:
                logging.info(f'Clicking link: {link['text']} {link['offset']} \n#{href}')
                logging.info(f'\n<!-- \noffset {text_offset} \n{page_info['body'][text_offset-50:text_offset+50]} \n-->\n')

                if open_new_tab:
                    page = page.context.new_page()
                    page.goto(href)
                    page_cache.append({'url': page_info['url'], 'page': page, 'body': page_info['body'], 'links': page_info['links'], 'title' : page_info['title']})
                else:
                    if ('reader_stop_event' in page_info and page_info['reader_stop_event'] is not None):
                        page_info['reader_stop_event'].set() #stop any reading.
                    logger.info(f'Using existing tab to go to {href}')
                    return read_page(href, cacheno) #use same tab
                return True
            else:
                logging.warning(f'Link {linkno} has no href')
        else:
            logging.warning(f'Link number {linkno} out of range')
    else:
        logging.warning(f'Cache number {cacheno} out of range')
    return False


def find_last(link_offset=1, cacheno=-1, text_offset=-1):
    """Go back to the previous page in the current cache."""
    global current_cache
    if (cacheno < 0):
        cacheno = current_cache
    if (link_offset == 0):  #go back one for default case.  
        link_offset = -1
    if cacheno >= 0 and cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        page = page_info['page']
        links = page_info['links']
    
        if (text_offset > 0):
            #find and jump to this link.  
            linkno = 0
            for i, link in enumerate(links):
                if 'offset' in link and link['offset'] <= text_offset:
                    linkno = i
            if (link_offset != 0):
                linkno += link_offset

            if linkno < len(links) and linkno >= 0:
                link = links[linkno]
                #jump to this link in page.  
                page.locator("text='" + link['text'] + "'").scroll_into_view_if_needed()
                logging.info(f'Jumping to link: {link['text']} {link['offset']} \n#{link['href']}')
                return 0
    return -1

def go_back(num=1, cacheno=-1):
    """Go back to the previous page in the current cache."""
    global current_cache
    if (cacheno < 0):
        cacheno = current_cache
    if (num == 0):  #go back one for default case.  
        num = 1
    if cacheno >= 0 and cacheno < len(page_cache):
        page = get_ppage(cacheno)
        for _ in range(num):
            page.go_back()

        logging.info(f'Went back to previous page in cache {current_cache}')
        body_text, link_data = get_page_details(page)
    #        await page.close()
    #        await browser.close()
        cacheno = cache_page(page.url, page, body_text, link_data, cacheno)
        current_cache = cacheno
        if (page.url not in page_cache[cacheno]['current_offset']):
            page_cache[cacheno]['current_offset'][page.url] = 0


        return body_text, link_data, page, cacheno
    else:
        logging.warning(f'No valid current cache to go back in')
        return False

def open_browser():
    global mybrowser
    global myplaywright
    if mybrowser is None:
        myplaywright = sync_playwright().start()
        args = ["--disable-blink-features=AutomationControlled"]
        mybrowser = myplaywright.chromium.launch(headless=False, args=args)  

#        async with Stealth().use_async(async_playwright()) as p:
#            browser_type = p.chromium
#            mybrowser = await browser_type.launch(headless=False, args=args)  
    return mybrowser

def close_browser():
    #for now complete reset.  
    global mybrowser
    global myplaywright
    global mycontext
    global current_cache
    global page_cache
    if mybrowser is not None:
        mybrowser.close()
    mybrowser = None
    myplaywright = None
    mycontext = None
    current_cache = -1
    page_cache = []
    return 0

def get_stop_event(cacheno=-1):
    global current_cache
    if cacheno >= 0 and cacheno < len(page_cache):
        return page_cache[cacheno]['reader_stop_event']
    
    return None
def set_reader_queue(q2, q3, stop_event, cacheno=-1):
    global current_cache
    if cacheno < 0:
        cacheno = current_cache
    if cacheno >= 0 and cacheno < len(page_cache):
        page_cache[cacheno]['reader_queue'] = q2
        page_cache[cacheno]['sim_queue'] = q3
        page_cache[cacheno]['reader_stop_event'] = stop_event
        return True

def get_ppage(cacheno=-1): #get playwright page from cacheno

    if cacheno >= 0 and cacheno < len(page_cache):
        page = page_cache[cacheno]['page']
    else:
        browser = open_browser()
        global mycontext
        if mycontext is None:
            mycontext = browser.new_context()
        page = mycontext.new_page()
    return page

def find_nth_occurrence(main_string, sub_string, n):
    """
    Finds the index of the nth occurrence of a substring within a main string.

    Args:
        main_string (str): The string to search within.
        sub_string (str): The substring to find.
        n (int): The desired occurrence number (1 for the first, 2 for the second, etc.).

    Returns:
        int: The starting index of the nth occurrence of the substring,
             or -1 if the nth occurrence is not found.
    """
    if n <= 0:
        return -1  # Invalid occurrence number

    start_index = 0
    occurrence_count = 0

    while occurrence_count < n:
        index = main_string.find(sub_string, start_index)
        if index == -1:
            return -1  # Substring not found enough times
        
        occurrence_count += 1
        if occurrence_count == n:
            return index
        
        start_index = index + len(sub_string) # Start searching after the found occurrence

    return -1 # Should not be reached if n > 0 and occurrence_count is handled correctly

def get_page_details(page):

    body_text = ""
    link_data = []
    last_link = None
    idx = 0
    logger.info(f'Getting page details for: {page.url}')
    #page.set_default_timeout(1000)
    try:
        """
        links_locator = page.locator('a')
        for i in range(links_locator.count()):
            link_element = links_locator.nth(i)
            href = link_element.get_attribute('href')
            text_content = link_element.text_content()
            bb = link_element.bounding_box()
            if href != last_link and href !="" and text_content is not None and text_content.strip() != '':
                idx += 1
                link_data.append({'href': href, 'text': text_content, 'bbox': bb, 'index': idx})        
                last_link = href
        """
        link_data = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            return links.map((link, index) => {
                const rect = link.getBoundingClientRect();
                return {
                    href: link.href,
                    text: link.innerText,
                    bbox: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    },
                    index: index
                };
            });
        }""")

        logger.info(f'Got Links for: {page.url}')
        print(link_data)
        body = page.locator('body')
        for i in range(body.count()):
            body_element = body.nth(i)

            body_text += body.inner_text()
#        print(body_text)
        logger.info(f'Got Body for: {page.url}')

        #iterate through and add offset for the link content
        #should create multiple links if multiple same text. For now we just get the last offset.  
        link_text_count = {}
        offset_found = 0
        for link in link_data:
            if link['text'] and link['href']:
                nth = link_text_count.get(link['text'], 0) + 1
                link_text_count[link['text']] = nth
                offset = find_nth_occurrence(body_text, link['text'], nth)
                if (offset == -1):
                    print(f"Could not find link text in body: {link['text']}")
                else:
                    offset_found += 1
                link['offset'] = offset

            else:
                print("Link with missing text or href")
                link['offset'] = -1
        #sort by offset.  
        link_data.sort(key=lambda x: x.get('offset'))
        #print(link_data)
        logger.info(f'Got page details with {len(body_text)} characters and {len(link_data)} links')

        return body_text, link_data
    except Exception as e:

        logging.error(f'Error getting page details: {e}')
        return body_text, link_data
    
def update_page_offset(cacheno=-1):
    global current_cache
    total_read = 0
    if (cacheno < 0):
        cacheno = current_cache
    q2 = page_cache[cacheno]['reader_queue']
    while (q2 is not None and not q2.empty()):
        total_read = q2.get() #get current link number.  
        #set offset
        page_cache[current_cache]['current_offset'][page_cache[current_cache]['page'].url] = total_read
    total_read = page_cache[cacheno]['current_offset'][page_cache[cacheno]['page'].url]
    return total_read

def cache_page(url, page, body_text, link_data, cacheno=-1):
    if cacheno >= 0 and cacheno < len(page_cache):
        page_cache[cacheno] = {'url': url, 'page': page, 'current_offset': {url: 0}, 'body': body_text, 'links': link_data, 'title' : page.title(), 'reader_queue': page_cache[cacheno].get('reader_queue', None), 'sim_queue': page_cache[cacheno].get('sim_queue', None), 'reader_stop_event': page_cache[cacheno].get('reader_stop_event', None)}            
    else:
        page_cache.append({'url': url, 'page': page, 'current_offset': {url: 0}, 'body': body_text, 'links': link_data, 'title' : page.title(), 'reader_queue': None, 'sim_queue': None, 'reader_stop_event': None})
        cacheno = len(page_cache) - 1
    return cacheno

def read_page(url, cacheno=-1):
    global current_cache
    """Search the web for a query using Playwright."""
    #fix relative URLs.  
    # Implement the web search logic here
    # This is a placeholder implementation

    page = get_ppage(cacheno)

    logging.info(f'Getting: {url}')

    base = page.url
    if (base.startswith('http')):
        parsed_base = base.split('/')
        base = parsed_base[0] + '//' + parsed_base[2]

    if url.startswith('/') and base is not None:
        url = base + url
    
    if (url != '' and not url.startswith('http')): #for now only http/https
        #bad URL
        logging.warning(f'Bad URL: {url}')
        return "", [], page, cacheno

    if (url != ''):
        page.goto(url, wait_until="domcontentloaded")
    logging.info(f'Page loaded: {page.url}')
    body_text, link_data = get_page_details(page)
#        await page.close()
#        await browser.close()
    cacheno = cache_page(url, page, body_text, link_data, cacheno)
    current_cache = cacheno
    logging.info(f'Cached page {cacheno} for URL: {url}')
    return body_text, link_data, page, cacheno


def search_web(query, engine=0, cacheno=-1):
    """Search the web for a query using Playwright."""
    logging.info(f'Searching the web for: {query}')
    # Implement the web search logic here
    # This is a placeholder implementation
    baseurl = "https://www.bing.com/news/search?q="
    print(f"Using search engine {engine}")
    if (engine == 1): #wiki
        baseurl = "https://en.wikipedia.org/w/index.php?search="
    elif (engine == 2): #yahoo
        baseurl = "https://search.yahoo.com/search?p="
    elif (engine == 3):
        baseurl = "https://duckduckgo.com/?q="
    elif (engine == 4):
        baseurl = "https://www.bing.com/search?q="
    elif (engine == 5):
        baseurl = "https://www.ecosia.org/search?q="
    elif (engine == 6):
        baseurl = "https://www.qwant.com/?q="
    elif (engine == 7):
        baseurl = "https://www.startpage.com/do/dsearch?query="
    elif (engine == 8):
        baseurl = "https://www.yandex.com/search/?text="
    elif (engine == 9):
        baseurl = "https://www.wikipedia.org/wiki/Special:Search?search="
    elif (engine == 10):
        baseurl = "https://news.google.com/search?q="
    elif (engine == 11):
        baseurl = "https://www.bing.com/news/search?q="

    url = f"{baseurl}{query}"
    body_text, link_data, page, cacheno = read_page(url, cacheno)

    return body_text, link_data, page, cacheno


def main():
    logging.basicConfig(filename='trey.log', 
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    with sync_playwright() as p:
        for browser_type in [p.chromium, p.firefox, p.webkit]:
            browser = browser_type.launch()
            page = browser.new_page()
            page.goto('http://playwright.dev')
            page.screenshot(path=f'example-{browser_type.name}.png')
            browser.close()

    text, links, page, cacheno = search_web("What is the capital of France?")  

    
if __name__ == "__main__":
    #asyncio.run(main())
    main()
