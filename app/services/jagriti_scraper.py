from fastapi import HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, Tag
import os
import time
from app.models import Case

SEARCH_PAGE_URL = "https://e-jagriti.gov.in/advance-case-search"

def get_selenium_driver(headless: bool = True):
    """Initializes and returns a Selenium Chrome driver for the Docker environment."""
    # In a Linux/Docker environment, Selenium finds the driver automatically from the system PATH.
    service = ChromeService()

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    
    # Standard options for stability in a containerized environment
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_states():
    """Fetches states by controlling a real browser with Selenium."""
    driver = get_selenium_driver(headless=True)
    try:
        driver.get(SEARCH_PAGE_URL)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "stateId"))
        )
        time.sleep(2)
        states_data = driver.execute_script("""
            return fetch('/e-jagriti/MasterController/getState', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'flag=1'
            }).then(response => response.json());
        """)
        states = [{"id": item[0], "name": item[1]} for item in states_data]
        return states
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Selenium error fetching states: {str(e)}")
    finally:
        driver.quit()

def get_commissions(state_id: str):
    """Fetches commissions using Selenium."""
    driver = get_selenium_driver(headless=True)
    try:
        driver.get(SEARCH_PAGE_URL)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "stateId"))
        )
        time.sleep(2)
        commissions_data = driver.execute_script(f"""
            return fetch('/e-jagriti/MasterController/getConsumerForum', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'stateId={state_id}'
            }}).then(response => response.json());
        """)
        commissions = [{"id": item[0], "name": item[1]} for item in commissions_data]
        return commissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Selenium error fetching commissions: {str(e)}")
    finally:
        driver.quit()

def search_cases(state_id: str, commission_id: str, search_by: str, search_value: str):
    """Performs a case search and scrapes the results, requiring manual CAPTCHA input."""
    # Headless is False so the user can see the browser window if running locally
    # or to allow interaction in the hosting service's shell if needed.
    driver = get_selenium_driver(headless=False)
    
    try:
        driver.get(SEARCH_PAGE_URL)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "stateId")))

        # --- Fill out the form ---
        driver.find_element(By.ID, "radDCDRC").click()
        driver.find_element(By.ID, "stateId").send_keys(state_id)
        time.sleep(1) # Wait for commissions to dynamically load
        driver.find_element(By.ID, "consumerForumId").send_keys(commission_id)
        driver.find_element(By.ID, "radMorAdvSear").click()
        time.sleep(0.5)
        driver.find_element(By.ID, "searchBy").send_keys(search_by)
        driver.find_element(By.ID, "searchText").send_keys(search_value)

        # --- Handle CAPTCHA ---
        print("\n--- ACTION REQUIRED ---")
        print("A browser window has opened. Please solve the CAPTCHA you see.")
        captcha_solution = input("Enter the CAPTCHA text here and press Enter: ")
        print("---------------------\n")
        driver.find_element(By.ID, "captcha").send_keys(captcha_solution)

        # --- Submit and wait for results ---
        driver.find_element(By.ID, "searchButton").click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "reportOrde")))
        
        # --- Scrape the results table ---
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", {"id": "reportOrde"})
        
        if not isinstance(table, Tag):
            return []

        cases = []
        tbody = table.find("tbody")
        
        if not isinstance(tbody, Tag):
            return []

        rows = tbody.find_all("tr")
        for row in rows:
            if not isinstance(row, Tag):
                continue

            cells = [cell.text.strip() for cell in row.find_all("td")]
            if len(cells) < 7:
                continue
            
            doc_link = None
            link_tag = row.find("a")
            if isinstance(link_tag, Tag) and link_tag.has_attr('href'):
                doc_link = f"{SEARCH_PAGE_URL}{link_tag['href']}"

            case_data = Case(
                filing_date=cells[0],
                case_stage=cells[1],
                case_number=cells[2],
                complainant=cells[3],
                respondent=cells[4],
                complainant_advocate=cells[5],
                respondent_advocate=None,
                document_link=doc_link
            )
            cases.append(case_data)
        
        return cases
    except Exception as e:
        driver.save_screenshot("error_screenshot.png")
        print(f"An error occurred. A screenshot has been saved to 'error_screenshot.png'")
        raise HTTPException(status_code=500, detail=f"Selenium error during search: {str(e)}")
    finally:
        driver.quit()