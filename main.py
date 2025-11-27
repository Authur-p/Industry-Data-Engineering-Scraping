import asyncio
import csv
from playwright.async_api import async_playwright

SEARCH_TERM = "oil and gas"


async def process_company(browser, company_info):
    """Process a single company in parallel"""

    context = await browser.new_context()
    company_page = await context.new_page()

    try:
        await company_page.goto(f"https://finelib.com{company_info['href']}", wait_until="domcontentloaded")
        # await company_page.wait_for_load_state("networkidle")
        await company_page.wait_for_selector("div.bx-inner")

        # await company_page.wait_for_selector("div.cmpny-lstng url a", timeout=10000)
        
        url = company_page.url
        # desc = (await company_page.inner_text("div.main-content"))[:500]
        
        return {
            "company_name": company_info["name"],
            "source_url": url,
            "address": await company_page.text_content('[itemprop="streetAddress"]') if await company_page.text_content('[itemprop="streetAddress"]').count() > 0 else None,
            'city': await company_page.text_content('[itemprop="addressLocality"]') if await company_page.text_content('[itemprop="addressLocality"]').count() > 0 else None,
            "phone": await company_page.locator('[itemprop="telephone"] a').all_text_contents() if await company_page.locator('[itemprop="telephone"] a').count() > 0 else None,
            "website": await company_page.get_attribute("div.cmpny-lstng a", 'href') if await company_page.locator("div.cmpny-lstng a").count() > 0 else None
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
        
        while True:
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



            # Next page logic
            # next_button = await page.query_selector("a:has-text('Next')")
            # if next_button:
            #     try:
            #         # Try to click with short timeout
            #         print("→ Attempting to go to next page…")
            #         async with page.expect_navigation(timeout=30000):
            #             await next_button.click()
            #         print("✓ Successfully navigated to next page")
            #     except Exception as e:
            #         print(f"Next button not clickable: {e}")
            #         print("No more pages.")
            #         break
            # else:
            #     print("No next button found.")
            #     break


            # next_button = await page.query_selector("a:has-text('Next')")
            # if next_button:
            #     # Get current URL before clicking
            #     current_url = page.url
                
            #     print("→ Attempting to go to next page…")
            #     await next_button.click()
                
            #     # Wait for potential navigation with shorter timeout
            #     try:
            #         await page.wait_for_url(lambda url: url != current_url, timeout=5000)
            #         print("✓ Successfully navigated to next page")
            #     except Exception as e:
            #         print(f"No navigation occurred - already on last page: {e}")
            #         print("No more pages.")
            #         break
            # else:
            #     print("No next button found.")
            #     break

            


            # next_button = await page.query_selector("a:has-text('Next')")
            # if next_button:
            #     current_url = page.url
                
            #     print("→ Attempting to go to next page…")
            #     await next_button.click()
                
            #     # Wait a bit for potential navigation, then check
            #     await asyncio.sleep(3000)  # Wait 3 seconds
                
            #     if page.url != current_url:
            #         print("✓ Successfully navigated to next page")
            #     else:
            #         print("URL didn't change - no more pages.")
            #         break
            # else:
            #     print("No next button found.")
            #     break


            # Try to find "Next" button
            next_button = await page.query_selector("a:has-text('Next')")

            if not next_button:
                print("No 'Next' button — last page reached.")
                break

            # Check if the button is disabled or has no href (common when it's the last page)
            href = await next_button.get_attribute("href")
            if not href or href.strip() == "" or href == "#":
                print("Next button exists but is not clickable (probably last page).")
                break

            # If button is valid → click it without expecting navigation
            print("→ Going to next page…")
            await next_button.click()
            await page.wait_for_load_state("load")
            print("✓ Moved to next page successfully")



        await browser.close()
        # print(all_items)

        with open("companies.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "url"])
            writer.writeheader()
            writer.writerows(all_items)

        return all_items

# Run async function
asyncio.run(async_scraping())