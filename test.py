import asyncio
from playwright.async_api import async_playwright

SEARCH_TERM = "oil and gas"

async def process_company(browser, company_info):
    """Process a single company in parallel"""
    context = browser.contexts[0]
    company_page = await context.new_page()
    print('here')
    
    try:
        await company_page.goto(f"https://finelib.com{company_info['href']}")
        print('this')
        await company_page.wait_for_load_state("networkidle")
        
        # Wait for content to load with timeout
        try:
            await company_page.wait_for_selector("div.bx-inner", timeout=10000)
        except:
            print(f"Timeout waiting for content on {company_info['name']}")
        
        url = company_page.url
        
        return {
            "name": company_info["name"],
            "url": url,
        }
    except Exception as e:
        print(f"Error processing {company_info['name']}: {e}")
        return None
    finally:
        await company_page.close()

async def extract_company_data(company_element):
    """Extract all data from a single company element"""
    name = await company_element.inner_text()
    href = await company_element.get_attribute('href')
    return {"name": name.strip(), "href": href}

async def async_scraping():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://finelib.com/")
        
        # Type search term and submit
        await page.fill("input[name='q']", SEARCH_TERM)
        await page.click("input[type='image']")

        # Better waiting strategies
        try:
            # Wait for search results container
            await page.wait_for_selector("#search-result-cnt", timeout=15000)
            
            # Wait a bit more for dynamic content
            await page.wait_for_timeout(2000)
            
            # Alternative: wait for any company links to appear
            await page.wait_for_selector("#search-result-cnt dl dt a", timeout=10000)
        except Exception as e:
            print(f"Error waiting for search results: {e}")
            await browser.close()
            return []

        all_items = []

        # Get all company URLs with better error handling
        companies = await page.query_selector_all("#search-result-cnt dl dt a")
        
        if not companies:
            print("No companies found! Let's check what's actually on the page:")
            # Debug: check what's in the search results
            search_content = await page.text_content("#search-result-cnt")
            print(f"Search result content: {search_content[:500]}...")
            
            # Alternative selectors
            alt_selectors = [
                ".search-results a",
                ".result-item a", 
                "dt a",
                "a[href*='/companies/']"
            ]
            
            for selector in alt_selectors:
                alt_companies = await page.query_selector_all(selector)
                if alt_companies:
                    print(f"Found {len(alt_companies)} companies with selector: {selector}")
                    companies = alt_companies
                    break

        print(f"Found {len(companies)} companies")
        
        if not companies:
            await browser.close()
            return []

        company_info = await asyncio.gather(*[extract_company_data(company) for company in companies])
        print(f"Company URLs: {company_info}")

        # Process companies in parallel with error handling
        tasks = [process_company(browser, info) for info in company_info]
        page_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and None results
        for result in page_results:
            if not isinstance(result, Exception) and result is not None:
                all_items.append(result)

        await browser.close()
        print(f"Successfully processed {len(all_items)} companies")
        print(all_items)

        return all_items

# Run async function
asyncio.run(async_scraping())