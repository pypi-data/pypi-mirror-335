import time
import webbrowser
import pyautogui
import pyperclip
from urllib.parse import quote_plus  # Important for URL encoding



def start_chrome(url="google.com"):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    webbrowser.open_new(url)

def write(text):
    time.sleep(0.5)
    pyautogui.write(text)


def press(*keys):
    if len(keys) == 1:
        pyautogui.press(keys[0])
    else:
        pyautogui.hotkey(*keys)


def get_page_html():
    # View page source
    time.sleep(0.5)

    press('ctrl', 'u')
    time.sleep(0.5)

    # Select all and copy
    press('ctrl', 'a')
    time.sleep(0.5)
    press('ctrl', 'c')
    time.sleep(0.5)

    # Get the copied HTML
    html = pyperclip.paste()

    # Close the source view tab
    press('ctrl', 'w')
    return html



import re
from bs4 import BeautifulSoup


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def process_google_search_html(html_content,advanced=False):
    """
    Processes the HTML content of a Google search results page to extract
    information about standard web search results (URL, title, description).
    Uses robust selectors to handle variations in Google's HTML structure.

    Args:
        html_content: The HTML content of the page as a string.

    Returns:
        A list of dictionaries, where each dictionary represents a search result
        and contains: 'url', 'title', and 'description'.  Returns an empty
        list on failure or if no standard web results are found.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the main result container. The ID 'rso' seems to be more consistently
        # used for the section containing the main search results.
        main_results_container = soup.find(id='rso')

        if not main_results_container:
            print("Error: Main search results container (id='rso') not found.")
            return []

        # Now, find all search result containers *within* the main container.
        # We use find_all on the main_results_container, *not* on the whole soup.
        result_containers = main_results_container.find_all('div', class_='g')

        results = []

        for container in result_containers:
            # Extract URL
            link = container.find('a', href=True)
            url = link['href'] if link else None

            if advanced:
                # Extract Title
                title_tag = container.find('h3')
                title = title_tag.get_text(separator=" ", strip=True) if title_tag else None

                # Extract Description (Robust - handles multiple cases)
                description = None  # Initialize to None

                # 1. Try the span with class="aCOpRe" (more specific, preferred)
                description_tag = container.find('span', class_='aCOpRe')
                if description_tag:
                    description = description_tag.get_text(separator=" ", strip=True)
                    # print("Found with aCOpRe") # Debug print

                # 2. If that fails, try the div with style (less specific, fallback)
                if not description:
                    description_tag = container.find('div', style=lambda value: value and 'line-height:1.58' in value)
                    if description_tag:
                        description = description_tag.get_text(separator=" ", strip=True)
                        # print("Found with style") # Debug print

                #  3. One more fallback, that gets a lot more.  Look for *any* div
                #     with class 'VwiC3b' inside the result container.  This is
                #     less precise, but more comprehensive.
                if not description:
                    description_tag = container.find('div', class_='VwiC3b')
                    if description_tag:
                        description = description_tag.get_text(separator=" ", strip=True)
                        # print("Found with VwiC3b") # Debug print
            if url and (not advanced):
                results.append(url)
            elif url and title and description:
                results.append(SearchResult(
                    url=url, title=title, description=description
                ))
            else:
                pass

        return results

    except Exception as e:
        print(f"Error during processing: {e}")
        return []


def extract_https_links(html_content,advanced=True):
    soup = BeautifulSoup(html_content, 'html.parser')
    https_links = []
    for element in soup.find_all(href=True):
        if 'https://' in element['href']:
            if 'google' in element['href']: continue
            if element['href'] and not advanced:
                https_links.append(element['href'])
            else:
                https_links.append(SearchResult(
                title= element.text.strip(),
                description= element.text.strip(),
                url= element['href']
            ))

    return https_links

def google(query,advanced=False,max_urls:int=10):
    url = f"https://www.google.com/search?q={quote_plus(query)}&num={max_urls}"
    start_chrome(url)
    html = get_page_html()
    press('ctrl', 'w')
    res = extract_https_links(html,advanced=advanced)
    return res[:max_urls]

if __name__ == '__main__':
    print(google('who is modi?'))
