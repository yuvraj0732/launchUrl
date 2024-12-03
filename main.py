from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import uvicorn

app = FastAPI()

# Configure CORS to allow any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define environment variables
env_vars = {   
 "AICORE_AUTH_URL": "https://sapit-core-playground-vole.authentication.eu10.hana.ondemand.com",
 "AICORE_CLIENT_ID": "sb-e280c7a4-3339-4ac0-a5c2-4a575e88025a!b313091|aisvc-662318f9-ies-aicore-service!b540",
 "AICORE_CLIENT_SECRET": "61d6191b-e485-4635-a225-00a6bae72fe6$1i1BIaGAbhN6uz_HNJ9_uzkEOf_U5h5BixBA0dHGWNQ=",
 "AICORE_RESOURCE_GROUP": "default",
 "AICORE_BASE_URL":    "https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com"
}
os.environ.update(env_vars)

# Request body for the POST endpoint
class RequestBody(BaseModel):
    url: str

# Global WebDriver instance to prevent it from closing
driver_instance = None

def get_driver():
    """Initialize and return a persistent WebDriver instance."""
    global driver_instance
    if driver_instance is None:
        options = Options()
        options.add_argument("--disable-gpu")
        # Uncomment the following line to run the browser in headless mode
        # options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        driver_instance = webdriver.Chrome(service=service, options=options)
        driver_instance.maximize_window()  # Maximize the browser window
    return driver_instance


@app.get("/")
async def root():
    return {"message": "Hello, Welcome to the Test Incidents Fast APIs."}

@app.post("/open_url/")
async def open_url(body: RequestBody):
    """Open a URL using Selenium WebDriver."""
    url = body.url
    try:
        driver = get_driver()
        driver.get(url)

        # Store the original window handle
        original_window = driver.current_window_handle
        print(f"Original window handle: {original_window}")

        # Wait for potential new windows to open
        driver.implicitly_wait(10)  # Adjust the timeout as needed

        # Get all window handles
        all_windows = driver.window_handles
        print(f"All window handles: {all_windows}")

        # Switch to the new window, if available
        for window in all_windows:
            if window != original_window:
                driver.switch_to.window(window)
                print(f"Switched to new window with handle: {window}")
                break

        # Return the title of the currently active window
        current_title = driver.title
        print(f"Current window title: {current_title}")

        return {"status": "success", "url": url, "title": current_title}
    except Exception as e:
        return {"status": "failure", "error": str(e)}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5058"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)