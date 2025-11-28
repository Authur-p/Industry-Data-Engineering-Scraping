import asyncio
import csv
from datetime import datetime, timezone
from playwright.async_api import async_playwright

SEARCH_TERM = "oil and gas"


async def process_company(browser, company_info):
    """Process a single company in parallel"""

    context = await browser.new_context()
    company_page = await context.new_page()

    try:
        await company_page.goto(f"https://finelib.com{company_info['href']}", wait_until="domcontentloaded", timeout=30000)
        # await company_page.wait_for_load_state("networkidle")
        await company_page.wait_for_selector("div.bx-inner")
        
        url = company_page.url
        # desc = (await company_page.inner_text("div.main-content"))[:500]

        phone = await company_page.locator('[itemprop="telephone"] a').all_text_contents()
        email_element = await company_page.query_selector('a[href^="mailto:"]')
        if email_element:
            email_href = await email_element.get_attribute('href')
            email = email_href.replace("mailto:", "").strip() if email_href else None
        else:
            email = 'NIL'
        
        return {
            "company_name": company_info["name"],
            "source_url": url,
            "address": await company_page.text_content('[itemprop="streetAddress"]') if await company_page.locator('[itemprop="streetAddress"]').count() > 0 else None,
            'city': await company_page.text_content('[itemprop="addressLocality"]') if await company_page.locator('[itemprop="addressLocality"]').count() > 0 else None,
            'state': await company_page.text_content('[itemprop="addressRegion"]') if await company_page.locator('[itemprop="addressRegion"]').count() > 0 else None,
            "phone": ", ".join([f"{text.replace(" ", "").strip()}" for text in phone]) if len(phone) > 1 else f"{phone[0].replace(" ", "").strip()}" if phone else None,
            "website": await company_page.get_attribute("div.cmpny-lstng a", 'href') if await company_page.locator("div.cmpny-lstng a").count() > 0 else None,
            "email": email
        }
    except Exception as e:
        print(f"Error processing {company_info['name']}: {str(e)}")
        # Return a valid dict with error info instead of None
        return {
            "company_name": company_info["name"],
            "source_url": f"https://finelib.com{company_info['href']}",
            "address": None,
            'city': None,
            'state': None,
            "phone": None,
            "website": None,
            'email': None,
            "error": str(e)
        }

    finally:
        await company_page.close()
        # await context.close()


async def extract_company_data(company_element):
    """Extract all data from a single company element"""
    try:
        name = await company_element.inner_text()
        href = await company_element.get_attribute('href')
        return {"name": name, "href": href}
    except Exception as e:
        print(f"Error extracting company data: {e}")
        return None 


async def async_scraping():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto("https://finelib.com/")

            # Type “oil and gas” into search bar
            await page.fill("input[name='q']", SEARCH_TERM)
            await page.click("input[type='image']") 

            # Wait for the results area
            await page.wait_for_selector("#search-result-cnt")
            # await page.wait_for_load_state("networkidle")
            
            all_items = []
            
            while True:
                # Get all company URLs first without clicking/navigating
                companies = await page.query_selector_all("#search-result-cnt dl dt a")

                company_info = await asyncio.gather(*[extract_company_data(company) for company in companies])
                # Filter out None values from extraction errors
                company_info = [ci for ci in company_info if ci is not None]

                # Process companies in parallel
                tasks = [
                        process_company(browser, company) 
                        for company in company_info
                    ]
                page_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Filter out any exceptions
                for result in page_results:
                    if not isinstance(result, Exception):
                        result["last_checked"] = datetime.now(timezone.utc).isoformat()
                        all_items.append(result)


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

            # Filter out any remaining None values
            valid_items = [item for item in all_items if item is not None]

            with open("companies.csv", "w", newline="", encoding="utf-8") as f:
                fieldnames = ['company_name', 'source_url', 'address', 'city', 'state', 'phone', 'website', 'email', 'last_checked']
                # Add error field if any items have it
                if any('error' in item for item in valid_items): fieldnames.append('error')  # DYNAMIC FIELDNAMES
                    
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(valid_items)

            print(f"Scraping completed. Saved {len(valid_items)} companies to companies.csv")
            return valid_items
        
        except Exception as e:
            print(f"Main scraping error: {e}")

# Run async function
asyncio.run(async_scraping())