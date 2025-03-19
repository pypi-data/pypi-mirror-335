from urllib.parse import urlparse, parse_qs, unquote
from playwright.async_api import async_playwright
from markitdown import MarkItDown
from bs4 import BeautifulSoup
from typing import List
import asyncio
import requests
from markdownify import markdownify

md = MarkItDown() 
def google_search(query) -> List[dict]:
    '''Returns the search results from DuckDuckGo. A list of dictionaries containing title, description and link'''
    # Build the search URL (note: you may want to urlencode the query in production)
    url = f"https://duckduckgo.com/html/?q={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    
    # Each result container has the class "result__body"
    for result in soup.select("div.result__body"):
        title_tag = result.select_one("h2.result__title a.result__a")
        if not title_tag:
            continue
        
        # Extract the title text
        title = title_tag.get_text(strip=True)
        
        # Get the redirect link from the title tag
        link = title_tag.get("href")
        # If the link starts with "//", prefix it with https:
        if link.startswith("//"):
            link = "https:" + link
        
        # DuckDuckGo returns a redirect URL.
        # Extract the real URL from the 'uddg' parameter.
        parsed_link = urlparse(link)
        if "duckduckgo.com" in parsed_link.netloc and parsed_link.path.startswith("/l/"):
            query_params = parse_qs(parsed_link.query)
            if "uddg" in query_params:
                link = unquote(query_params["uddg"][0])
        
        # Extract the description from the snippet element
        snippet_tag = result.select_one("a.result__snippet")
        description = snippet_tag.get_text(strip=True) if snippet_tag else ""
        
        results.append({
            "title": title,
            "description": description,
            "link": link
        })

    print(results)
    
    return results



async def read_document(url):
    '''Reads any document or url and returns the markdownified content'''
    # Check if the uel contains any extensions
    extension = url.split('.')[-1]
    if extension in ['pdf', 'docx', 'pptx', 'xlsx']:
        markdown = md.convert(url)  # Convert the document to markdown
        print(f'#{markdown.title}\n\n{markdown.text_content}')
        return f'#{markdown.title}\n\n{markdown.text_content}'

    extension = '.html'
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set headless=False for debugging
        
        # Create a new browser context with the desired user agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)  # Wait for the page to load completely
        await asyncio.sleep(5)  # Additional wait time for JavaScript to render
        
        html_content = await page.content()  # Get the rendered HTML content

        await browser.close()

        markdowned = markdownify(html_content)

        print(markdowned)
        return markdowned
    
        # MARKDOWNIT lib does not work with manual html
        # # Save to a temporary file for debugging
        # with tempfile.NamedTemporaryFile(suffix=f"{extension}", mode='w') as tmp_file:
        #     tmp_file.write(html_content)
        
        #     await browser.close()
        
        #     markdown = md.convert(source=tmp_file.name, file_extension='html')  # Convert HTML to markdown

        #     return f'#{markdown.title}\n\n{markdown.text_content}'



if __name__ == '__main__':
    import asyncio

    asyncio.run(read_document('https://www.arcgis.com/home/item.html?id=4d9e864a198f426ba359be57e5836d54'))
