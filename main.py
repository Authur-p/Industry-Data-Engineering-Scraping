import asyncio
from playwright.async_api import async_playwright

SEARCH_TERM = "oil and gas"


async def process_company(browser, company_info):
    """Process a single company in parallel"""
    print(1)
    # context = browser.contexts[0]
    # company_page = await context.new_page()

    context = await browser.new_context()
    company_page = await context.new_page()

    print(2)
    
    try:
        await company_page.goto(f"https://finelib.com{company_info['href']}", wait_until="domcontentloaded")
        # await company_page.wait_for_load_state("networkidle")
        await company_page.wait_for_selector("div.bx-inner")
        
        url = company_page.url
        # desc = (await company_page.inner_text("div.main-content"))[:500]
        
        return {
            "name": company_info["name"],
            "url": url,
            # "description": desc,
        }
    except Exception as e:
        print(e)

    finally:
        await company_page.close()


async def extract_company_data(company_element):
    """Extract all data from a single company element"""
    name = await company_element.inner_text()
    href = await company_element.get_attribute('href')
    return {"name": name, "href": href}


async def async_scraping():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://finelib.com/")

        # Type “oil and gas” into search bar
        await page.fill("input[name='q']", SEARCH_TERM)
        await page.click("input[type='image']") 

        # Wait for the results area
        await page.wait_for_selector("#search-result-cnt")
        # await page.wait_for_load_state("networkidle")

        # await page.wait_for_selector("#search-result-cnt", timeout=15000)
        # await page.wait_for_timeout(2000)
        # await page.wait_for_selector("#search-result-cnt dl dt a", timeout=10000)

        
        all_items = []

        # Get all company URLs first without clicking/navigating
        companies = await page.query_selector_all("#search-result-cnt dl dt a")

        company_info = await asyncio.gather(*[extract_company_data(company) for company in companies])
        # print(f"Found {len(companies)} companies with URLs: {company_info}")

        # Process companies in parallel
        tasks = [
                process_company(browser, company) 
                for company in company_info
            ]
        page_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out any exceptions
        for result in page_results:
            if not isinstance(result, Exception):
                all_items.append(result)

        await browser.close()
        print(all_items)

        return all_items

# Run async function
asyncio.run(async_scraping())