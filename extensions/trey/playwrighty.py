#library to manage web interaction.  
#>pip install playwright
#>playwright install
#>pip install asyncio
import asyncio
import random
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
import datetime

#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
import config 

logger = logging.getLogger(__name__)

page_cache = [] # this should include history of pages each time.  
#array of arrays with {query, page, body, links, title, reader_queue, sim_queue, reader_stop_event}
bookmarks = [] #list of {url, [total_read, total_read]}
mybrowser = None
myplaywright = None
mycontext = None

current_cache = -1 #current cache page we are on.

screen_position = (0,0,0,0) #x,y,width,height


def load(qapp=None):
    """Load the Playwright library and initialize the browser."""
    global mybrowser
    global myplaywright
    global mycontext
    global screen_position

    logger.info('Loading Playwright library')
    if qapp is not None:
        #connect to signals
        primary_screen = qapp.primaryScreen()
        screens = qapp.screens()
        for i, s in enumerate(screens):
            if (s.name() != primary_screen.name()):
                logger.info(f'PScreen {i}: {s.name()} - PSize: {s.size()}')
                screen_position = (s.geometry().x(), s.geometry().y(), s.geometry().width(), s.geometry().height())

#    open_browser()
    return 0

def get_url(cacheno=-1):
    """Get URL from the cached page."""
    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        return page_info['url']
    else:
        logging.warning(f'Cache number {cacheno} out of range')
        return ""
    
def get_text(cacheno=-1, total_read=0, duration=5):
    """Get text from the cached page starting at total_read offset."""
    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        body = page_info['body']
        if (total_read > len(body)):
            total_read = (len(body) - duration*12)
        if (total_read - duration*12 < 0):
            total_read = duration*12
            
        
        text_chunk = body[total_read-duration*12:total_read]
        return text_chunk
    else:
        logging.warning(f'Cache number {cacheno} out of range')
        return "", total_read



def get_links(cacheno=-1, text_offset=0):
    """Get link offset from the cached page based on text offset."""
    global current_cache
    ret = []
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    linkno = 0
    if cacheno > -1 and cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        links = page_info['links']
        for i, link in enumerate(links):
            if 'offset' in link and link['offset'] <= text_offset:
                linkno = i
    else:
        logging.warning(f'Cache number {cacheno} out of range')

    for i in range(min(linkno-10, 0), linkno):
        ret.append(links[i])
    return ret

#text_offset is how far into the text we are.  link_offset is which link to click relative to that we want to click.
#usually this will be 0 or -1 to go back one link.

def get_link_number(cacheno=-1, text_offset=0, link_offset=0):
    """Get link from the cached page based on text offset and link offset."""
    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache

    if cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        page = page_info['page']
        url = page.url
        links = page_info['links']
        linkno = 0
        for i, link in enumerate(links):
            if 'offset' in link and link['offset'] <= text_offset:
                linkno = i
        if (link_offset != 0):
            linkno += link_offset

#        while (linkno < len(links)-1 and (links[linkno]['href'].startswith(url + "#") or links[linkno]['href'].startswith('#'))):
            #for now skip internal links.  
            #really want to jump to this text location..
#            linkno += 1            
        return linkno
    else:
        logging.warning(f'Cache number {cacheno} out of range')
    return -1


def is_internal_link(linkno, cacheno=-1):
    links = page_cache[cacheno]['links']
    orig_url = page_cache[cacheno].get('orig_url', '')
    url = page_cache[cacheno]['page'].url
    if (linkno < len(links)-1 and (links[linkno]['href'].startswith(url + "#") or links[linkno]['href'].startswith(orig_url+"#") or links[linkno]['href'].startswith('#'))):
        return True

def click_link(cacheno, text_offset, link_offset=0, open_new_tab=False):

    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache

    if (text_offset < 0):
        text_offset = 0
    

    """Click a link on a cached page."""
    if cacheno < len(page_cache):
        linkno = get_link_number(cacheno, text_offset, link_offset)
        if (linkno < 0):
            return False

        page_info = page_cache[cacheno]
        links = page_info['links']

        if (is_internal_link(linkno, cacheno)):
            #find href and return offset of this text..
            logger.info(f'Link {linkno} is an internal link, jumping to it in page')
            id = links[linkno]['href'].split('#')[-1]
            internal_info = page.locator(f"#{id}")
            inner_text = internal_info.inner_text()
            #jump to here in page temporarily.. 
            try:
                internal_info.scroll_into_view_if_needed()
            except Exception as e:
                logging.error(f'Error scrolling to internal link: {e}')
            return inner_text
        
        logger.info(f"Clicking on {links[linkno]['href'] if linkno < len(links) else 'No link'}")

        if linkno < len(links) and linkno >= 0:
            link = links[linkno]
            href = link['href']
            if href:
                #is internal link?
                
                
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


def get_bookmark(url, cacheno=-1):
    global bookmarks
    found_item = next(filter(lambda item: item.get("url") == url, bookmarks), None)
    if (found_item is not None):
        return found_item['total_read'][0]
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if (page_cache[cacheno]['current_offset'] is not None and url in page_cache[cacheno]['current_offset']):
        return page_cache[cacheno]['current_offset'][url]
    
    return 0


def get_bookmark_at_index(index):
    #only positive for now.  
    global bookmarks
    if (index >= 0 and index < len(bookmarks)):
        return bookmarks[index]
    return None

def remove_bookmark_at_index(index):
    #only positive for now.  
    global bookmarks
    if (index >= 0 and index < len(bookmarks)):
        bookmarks.pop(index)
        return True
    return False

def add_bookmark(url, total_read, text=""):
    global bookmarks
    logger.info(f'Adding bookmark for {url} at offset {total_read}')
    found_item = next(filter(lambda item: item.get("url") == url, bookmarks), None)
    body_length = page_cache[current_cache]['length'] if current_cache >=0 and current_cache < len(page_cache) else 0
    if (found_item is not None):
        found_item['total_read'].insert(0, total_read)
        found_item['text'].insert(0, text)
        bookmarks.remove(found_item)
        bookmarks.insert(0, found_item)
    else:
        bookmarks.insert(0, {'url': url, 'total_read': [total_read], 'length': body_length, 'text': [text]})
#        bookmarks.append({'url': url, 'total_read': [total_read], 'length': body_length})
    return 0


def get_skip_from_offset(offset=0, cacheno=-1):
    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        body = page_info['body']
        url = page_info['page'].url
        current_offset = page_info['current_offset'][url] if url in page_info['current_offset'] else 0
        orig_line_no = body.count('\n', 0, current_offset) + 1
        print(f'Current offset: {current_offset}, line number: {orig_line_no}')
        line_no = body.count('\n', 0, offset) + 1
        print(f'Target offset: {offset}, line number: {line_no}')
        total = len(page_info['found_positions'])
        current_tofind = page_info.get('current_tofind_index', -1)
        return line_no - orig_line_no-2, current_tofind, total #-1 to start at previous line
    else:
        logging.warning(f'Cache number {cacheno} out of range')
        return -1, -1, -1
    
def pprev(text, cacheno=-1):
    return pnext(text, cacheno, direction=-1)

def pnext(text, cacheno=-1, direction = 1):
    global current_cache
    print(f"searching for next occurrence of text: {text}")
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if cacheno >= 0 and cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        page = page_info['page']
        body = page_info['body']
        if (page_info['tofind'] != text):
            print(f"Text to find changed from {page_info['tofind']} to {text}, calling pfind")
            return pfind(text, cacheno)


        positions = page_info.get('found_positions', [])
        current_index = page_info.get('current_tofind_index', -1)
        if (current_index < 0 or current_index >= len(positions)):
            if (len(positions) > 0):
                current_index = 0 if direction == 1 else len(positions) - 1
            else:
                return -1

        if (direction == 1):
            page_info['current_tofind_index'] = current_index + 1
        else:
            page_info['current_tofind_index'] = current_index - 1
        logger.info(f'Finding text: {text} at offset {positions[current_index]}')
        #jump to this link in page.  if we have repetitive text, can potentially be problematic..
        ftext = body[positions[current_index]: positions[current_index]+len(text)*2]
        locator = page.get_by_text(ftext, exact=True)
        if (locator.count() == 0):
            boo = 1
        else:
            locator.scroll_into_view_if_needed()
            logger.info(f'Jumping to text: {ftext} at offset {positions[current_index]}')
            print(f"Jumped to text: {ftext} at offset {positions[current_index]}")
        return positions[current_index]
    return -1

def pfind(text, cacheno=-1):
    #find in page top level header with this text.  
    #get the line number where we see this text.  
    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    print(f"searching for text: {text} in page cache {cacheno}")

    if cacheno >= 0 and cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        page = page_info['page']
        body = page_info['body']
        #find all instances..
        positions = []

        # Iterate over all non-overlapping matches
        import re
        for match in re.finditer(text, body, re.IGNORECASE):
            positions.append(match.start()) # Get the starting index of the match
                    
        page_info['found_positions'] = positions
        page_info['tofind'] = text
        if len(positions) == 0:
            logger.info(f'No occurrences of text: {text} found')
            print(f"Could not find text: {text} in page")
            page_info['current_tofind_index'] = -1
            return -1
        page_info['current_tofind_index'] = 0
        offset = positions[ page_info['current_tofind_index'] ] if len(positions) > 0 else -1
        return pnext(text, cacheno)

    return -1

def find_last(link_offset=1, cacheno=-1, text_offset=-1):
    """Go back to the previous page in the current cache."""
    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
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
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if (num == 0):  #go back one for default case.  
        num = 1
    if cacheno >= 0 and cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        page = get_ppage(cacheno)
        for _ in range(num):
            page.go_back()
        if ('reader_stop_event' in page_info and page_info['reader_stop_event'] is not None):
            page_info['reader_stop_event'].set() #stop any reading.
        logger.info(f'Using existing tab to go to {page.url}')
        return read_page(page.url, cacheno) #use same tab

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
    global screen_position
    if mybrowser is None:
        myplaywright = sync_playwright().start()
        
#        args = ["--disable-blink-features=AutomationControlled", "--load-extension=C:\devinpiano\music\extensions\handsfree"]
        args = ["--disable-blink-features=AutomationControlled"]
        x = screen_position[0]
        y = screen_position[1]
        w = screen_position[2]
        h = screen_position[3]
        #f"--window-position={x_position},{y_position}", "--window-size=1000,800"
        args.append(f"--window-position={x},{y}")
        args.append(f"--window-size={w},{h}")
        logger.info(f'Launching browser at position {x},{y} size {w}x{h}')
        mybrowser = myplaywright.chromium.launch(headless=False, args=args)  

#        async with Stealth().use_async(async_playwright()) as p:
#            browser_type = p.chromium
#            mybrowser = await browser_type.launch(headless=False, args=args)  
    return mybrowser


def save_screenshot(cacheno=-1, lang="video"):
    page = get_ppage(cacheno)
    now = datetime.now()
    folder = f'../transcripts/{lang}/' 
    fname = f'{now.strftime('%Y%m%d_%H%M%S')}.png'
    if (page is not None):
        page.screenshot(path=folder + fname)
        return folder + fname

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


def play_video(cacheno=-1):
    global current_cache
    total_read = 0
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        return -1
    page = page_cache[cacheno]['page']
    #more complex with multiple video controls..
    page.evaluate("""() => {
        const video = document.querySelector('video');
        if (video) {
            video.play();
        }
    }""")


def get_page_details(page):

    body_text = ""
    link_data = []
    alt_text_data = []
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

        #remove single char links..
        link_data = [link for link in link_data if link['text'] and link['href'] and len(link['text'].strip()) > 1 and len(link['href'].strip()) > 1]
        alt_text_data = page.evaluate("""() => {
            const images = Array.from(document.querySelectorAll('img'));
            return images.map((img, index) => {
                const rect = img.getBoundingClientRect();
                return {
                    src: img.src,
                    alt: img.alt,
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
        logger.info(f'Got Alt Text for: {page.url}')
        print(alt_text_data)

        body = page.locator('body')
        for i in range(body.count()):
            body_element = body.nth(i)

            body_text += body.inner_text()
#        print(body_text)
        logger.info(f'Got Body for: {page.url}')

        #iterate through and add offset for the link content
        #should create multiple links if multiple same text. For now we just get the last offset.  
        link_text_count = {}
        link_last_offset = {}
        offset_found = 0
        offset_notfound = 0
        for link in link_data:
            if link['text'] and link['href']:
                nth = link_text_count.get(link['text'], 0) + 1
                link_text_count[link['text']] = nth
                offset = find_nth_occurrence(body_text, link['text'], nth)
                link_last_offset[link['text']] = offset
                if (offset == -1):
#                    print(f"Could not find link text in body: {link['text']}")
                    offset_notfound += 1
                else:
                    offset_found += 1
                link['offset'] = offset

            else:
                #print("Link with missing text or href")
                link['offset'] = -1
        #sort by offset.  
        link_data.sort(key=lambda x: x.get('offset'))
        #print(link_data)
        logger.info(f'Got page details with {len(body_text)} characters and {len(link_data)} links')
        logger.info(f'Found offsets for {offset_found} links, could not find offsets for {offset_notfound} links')
        body_text = '$$TITLE=' + page.title() + '\n' + body_text

        return body_text, link_data, alt_text_data
    except Exception as e:

        logging.error(f'Error getting page details: {e}')
        return body_text, link_data, alt_text_data
    
def update_page_offset(cacheno=-1):
    global current_cache
    total_read = 0
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        return total_read
    q2 = page_cache[cacheno]['reader_queue']
    url = page_cache[cacheno]['page'].url
#    print("Updating page offset for URL:", url)
    while (q2 is not None and not q2.empty()):
        total_read = q2.get() #get current link number.  
        #set offset
        page_cache[cacheno]['current_offset'][url] = total_read
        
        if (random.random() < 0.1):
            logging.info(f'Updated page offset for URL: {url} to {total_read}')

    if (total_read > 0):
        found_item = next(filter(lambda item: item.get("url") == url, bookmarks), None)
        if (found_item is not None):
            #this is temporary info, how to distinguish temporary vs permanent bookmarks?  
            found_item['total_read'].insert(0, total_read)

    if (total_read > 0):    #something was in queue...
        linkno = get_link_number(cacheno, total_read, 0) #update link offsets.
        #scroll into view
        if (linkno >= 0):
            page = page_cache[cacheno]['page']
            links = page_cache[cacheno]['links']
            if (linkno != page_cache[cacheno].get('current_link', -1)):
                # or page_cache[cacheno].get('last_total_read', links[linkno]['offset']) <= total_read-100): 
                page_cache[cacheno]['last_total_read'] = total_read
                #jump if we have read too much or have a new link.
                link = links[linkno]
                futurelink = links[linkno+2] if (linkno + 2 < len(links)) else None
                try:
                    page_cache[cacheno]['current_link'] = linkno
                    #this only gets exact matches, probably what we want, so we dont jump around the page too much.
                    #ideally detect the correct link based on location..
                    temptext = page_cache[cacheno]['body']

                    offset = link['offset']
                    off2 = temptext.rfind("\n", 0, offset)
                    if (off2 < offset-100):
                        temptext = temptext[offset-50: offset]
                    else:
                        offset = temptext.find("\n", offset)
                        if (offset < 0):
                            offset = off2
                        temptext = temptext[offset: offset+50]
                    #find text in the page..
                    locator = page.get_by_text(temptext)
                    if (locator.count() > 0):
                        locator.scroll_into_view_if_needed()
                    if link is not None:
                        #try partial match
                        locator = page.get_by_role("link", name=link['text'])
                        locator.highlight()
#                    if (locator.bounding_box() is not None and locator.bounding_box().get('height', 400) < 400):
#                        locator.highlight() #dont highlight the whole page..

#                    page.locator("a:has-text('" + link['text'] + "')").scroll_into_view_if_needed()
                    logging.info(f'Updated page scroll to link: {link["text"]} {link["offset"]} \n#{link["href"]}')
                except Exception as e:
                    jumped = False
                    #dont log all partial match failures..
                    logging.error(f'Error scrolling to link: {link["text"]} - {e}')


    total_read = page_cache[cacheno]['current_offset'][url]

    return total_read

def cache_page(url, page, body_text, link_data, cacheno=-1):
    if cacheno >= 0 and cacheno < len(page_cache):
        page_cache[cacheno] = {'url': url, 'page': page, 'current_offset': {url: 0}, 'body': body_text, 'links': link_data, 'title' : page.title(), 'reader_queue': page_cache[cacheno].get('reader_queue', None), 'sim_queue': page_cache[cacheno].get('sim_queue', None), 'reader_stop_event': page_cache[cacheno].get('reader_stop_event', None)}            
    else:
        page_cache.append({'url': url, 'page': page, 'current_offset': {url: 0}, 'body': body_text, 'links': link_data, 'title' : page.title(), 'reader_queue': None, 'sim_queue': None, 'reader_stop_event': None})
        cacheno = len(page_cache) - 1
    return cacheno

def get_bookmark_list():
    global bookmarks
    info = ""
    for i, bm in enumerate(bookmarks):

        info += f"$$BOOKMARK{i}=URL:{bm['url']} OFFSET:{bm['total_read'][0]} LENGTH:{bm['length']}\n"
        if (i >= 9):
            break #only first 10 for now.
    return info

def get_browser_info():
    #get current open tabs and URLs
    global current_cache
    info = ""
    if (current_cache >=0 and current_cache < len(page_cache)):
        page = page_cache[current_cache]['page']
        context = page.context
        pages = context.pages
        info += f"$$TABS={len(pages)}\n"
        for i, p in enumerate(pages):
            #wait for load state
            p.wait_for_load_state("domcontentloaded", timeout=1000)
            info += f"$$TAB{i}={p.title()}\n"
            info += f"$$TABURL{i}={p.url}\n"

    info += get_bookmark_list()
    return info

def detect_language(cacheno=-1):
    """Detect the language of the cached page."""
    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
    if cacheno < len(page_cache):
        page_info = page_cache[cacheno]       
        page = page_info['page']
        lang = page.evaluate("() => document.documentElement.lang")
        logging.info(f'Detected language: {lang} for URL: {page.url}')
        return lang
    else:
        logging.warning(f'Cache number {cacheno} out of range')
        return ""
    
def read_page(url, cacheno=-1):
    global current_cache
    """Search the web for a query using Playwright."""
    #fix relative URLs.  
    # Implement the web search logic here
    # This is a placeholder implementation

    global current_cache
    if (cacheno < 0 or cacheno >= len(page_cache)):
        cacheno = current_cache
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
    orig_url = page.url
    logging.info(f'Page loaded: {page.url}')
    body_text, link_data, alt_text_data = get_page_details(page)
#        await page.close()
#        await browser.close()

    #pull prev offset if exists.  
    prev_offsets = {}
    if (cacheno >=0 and cacheno < len(page_cache) and page_cache[cacheno] is not None and 'current_offset' in page_cache[cacheno]):
        prev_offsets = page_cache[cacheno]['current_offset']

    cacheno = cache_page(url, page, body_text, link_data, cacheno)
    current_cache = cacheno
    
    page_cache[cacheno]['current_offset'] = prev_offsets
    page_cache[cacheno]['length'] = len(body_text)
    page_cache[cacheno]['alt_text'] = alt_text_data
    page_cache[cacheno]['orig_url'] = orig_url

    if (page.url not in page_cache[cacheno]['current_offset']):
        #get previous bookmark offset.
        page_cache[cacheno]['current_offset'][page.url] = get_bookmark(page.url)

    page_cache[cacheno]['page'].bring_to_front()
    logging.info(f'Cached page {cacheno} for URL: {url}')
    return body_text, link_data, page, cacheno


def get_engine(engine=0):
    """Get the name of the search engine based on its index."""
    enginename = "Bing News"
    if (engine == 1): #wiki
        enginename = "Wikipedia"
    elif (engine == 2): #yahoo
        enginename = "Yahoo"
    elif (engine == 3):
        enginename = "DuckDuckGo"
    elif (engine == 4):
        enginename = "Bing"
    elif (engine == 5):
        enginename = "Ecosia"
    elif (engine == 6):
        enginename = "Qwant"
    elif (engine == 7):
        enginename = "Startpage"
    elif (engine == 8):
        enginename = "Yandex"
    elif (engine == 9):
        enginename = "Wikipedia"
    elif (engine == 10):
        enginename = "Google News"
    elif (engine == 11):
        enginename = "Bing News"
    return enginename
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
