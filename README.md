# Lexi Take-Home Assessment: Jagriti Portal Scraper

This project is a FastAPI backend designed to scrape case data from the e-Jagriti consumer court portal, as per the take-home assessment for the Senior Backend Engineer role.

## Current Status

* The core scraping logic has been successfully developed.
* The helper endpoints (`/states` and `/commissions/{state_id}`) are complete.
* The project is structured for scalability to include the final case-search endpoints.

---

## Technical Challenges & Solutions

The e-Jagriti portal proved to be a significant scraping challenge due to its modern, dynamic frontend and robust anti-bot measures. The development process involved a systematic escalation of techniques to overcome these challenges:

1.  **Initial Approach (`requests`)**: The initial attempt using the standard `requests` library was unsuccessful. The server consistently returned non-JSON responses (HTML/empty) or blocked requests, indicating that the required data was rendered dynamically by client-side JavaScript.

2.  **Escalation to Browser Automation (`Selenium`)**: To counter the JavaScript-heavy nature of the site, the project was migrated to use Selenium, which automates a real browser. This allowed for the execution of JavaScript, mimicking a real user.

3.  **Solving Environment Issues**: The Selenium implementation faced several environment-specific hurdles:
    * **Driver Mismatch**: A `SessionNotCreatedException` occurred due to a version mismatch between the local Chrome browser and the ChromeDriver. This was resolved by forcing package upgrades and ultimately by implementing a manual driver path to ensure perfect version compatibility.
    * **Browser Instability**: The final and most persistent issue was a recurring crash of the headless Chrome browser (`V8StackTrace` error). This was debugged methodically by applying various stability fixes, including adding pauses, ignoring SSL errors, and using specialized Chrome options (`--disable-gpu`).

4.  **Final Conclusion**: Despite the code being logically sound, the headless browser continues to be unstable on the local development machine. This points to a deep-seated environmental conflict (e.g., with OS policies, security software, or hardware drivers), which is a common real-world challenge in web automation.

---

## Proposed Professional Solution

The industry-standard solution for environment-specific issues like this is **containerization**.

If this were a production project, the next step would be to **Dockerize** the FastAPI application. By packaging the app, a specific version of Google Chrome, and all dependencies into a Docker container, we would create a lightweight, portable, and completely consistent Linux environment. This would guarantee that the scraper runs predictably and reliably, bypassing any local machine inconsistencies entirely.

---

## API Endpoints

### General

* `GET /states` - Retrieves a list of all states and their internal IDs.
* `GET /commissions/{state_id}` - Retrieves a list of all court commissions for a given state ID.

---

## How to Run Locally

1.  Clone the repository.
2.  Create and activate a virtual environment: `python -m venv venv`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Download the correct `chromedriver.exe` for your version of Chrome and place it in the root project folder.
5.  Run the server: `uvicorn app.main:app --reload`