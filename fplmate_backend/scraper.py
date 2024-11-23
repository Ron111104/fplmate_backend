from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def scrape(request):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (without UI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Setup the Chrome driver with the correct Service object
    service = Service(ChromeDriverManager().install())  # Use Service to manage the driver

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open the target website
        driver.get("https://www.premierinjuries.com/injury-table.php")
        
        # Wait for the page to load (you can customize the time or use explicit waits)
        time.sleep(5)  # Adjust sleep time if needed or use WebDriverWait
        
        # Extract data (for example, extract table data)
        injuries_data = []
        
        # Find the table (this is just an example; adjust the selector based on the actual HTML structure)
        table = driver.find_element(By.XPATH, "//table[@class='injury-table']")  # Adjust selector as needed
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        for row in rows[1:]:  # Skipping the header row
            cols = row.find_elements(By.TAG_NAME, "td")
            injury = {
                "player": cols[0].text,
                "team": cols[1].text,
                "injury_type": cols[2].text,
                "return_date": cols[3].text,
            }
            injuries_data.append(injury)
        
        # Return the scraped data as JSON
        return JsonResponse({"data": injuries_data})
    
    finally:
        driver.quit()  # Close the browser
