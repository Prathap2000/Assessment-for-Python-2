import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Companies list
comp = [
    'https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0',  # Microsoft
    'https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441',  # Google
    'https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1586&position=1&pageNum=0'  # Amazon
]

# Custom condition for checking attribute
def attribute_to_be(driver, locator, attribute, value):
    element = driver.find_element(*locator)
    return element.get_attribute(attribute) == value

# LinkedIn Scraping using Selenium
def scrape_linkedin_jobs():
    all_job_listings = []
    
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for url in comp:
        job_listings = []
        driver.get(url)
        time.sleep(5)  # Wait for page to load
        
        # Apply "Past week" filter
        try:
            # Click the filter button to open dropdown
            any_time_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Date posted filter. Any time filter is currently applied')]")
            any_time_button.click()
            time.sleep(2)  # Wait for dropdown to expand
            
            # Select "Past week" option
            past_week_option = driver.find_element(By.XPATH, "//label[contains(text(), 'Past week')]")
            past_week_option.click()
            
            # Click the "Done" button to apply the filter
            done_button = driver.find_element(By.XPATH, "//button[@class='filter__submit-button' and @data-tracking-control-name='public_jobs_f_TPR']")
            done_button.click()
            time.sleep(5)  # Wait for page to update with the filter applied
        except Exception as e:
            print(f"Error applying filter: {e}")
            continue
        
        # Scroll down to load more jobs
        while len(job_listings) < 50:
            # Locate job title elements
            job_elements = driver.find_elements(By.CSS_SELECTOR, 'div.base-card')
            for job in job_elements:
                if len(job_listings) >= 50:
                    break
                try:
                    title_element = job.find_element(By.CSS_SELECTOR, 'h3.base-search-card__title')
                    title = title_element.text
                    company_element = job.find_element(By.CSS_SELECTOR, 'h4.base-search-card__subtitle')
                    company = company_element.text
                    location_element = job.find_element(By.CSS_SELECTOR, 'span.job-search-card__location')
                    location = location_element.text
                    date_element = job.find_element(By.CSS_SELECTOR, 'time.job-search-card__listdate')
                    date = date_element.get_attribute('datetime')

                    job_listings.append({
                        "company_name": company,
                        "title": title,
                        "location": location,
                        "date_posted": date
                    })
                except Exception as e:
                    continue
            
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new jobs to load

        all_job_listings.extend(job_listings[:50])

    driver.quit()
    
    return all_job_listings

# Save data to CSV
def save_to_csv(data, filename):
    if not data:
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

# Save data to JSON
def save_to_json(data, filename):
    with open(filename, 'w') as output_file:
        json.dump(data, output_file, indent=4)

# Main execution
if __name__ == "__main__":
    # Scrape LinkedIn jobs
    linkedin_jobs = scrape_linkedin_jobs()
    save_to_csv(linkedin_jobs, 'linkedin_jobs.csv')
    save_to_json(linkedin_jobs, 'linkedin_jobs.json')
