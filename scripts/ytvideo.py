from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Chrome options
options = Options()
options.add_argument('--headless')  # Run in headless mode

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)

# URL of the YouTube video to be played
youtube_url = 'https://www.youtube.com/watch?v=XALBGkjkUPQ'
driver.get(youtube_url)

# Wait for the video to load and play
try:
    # Start time
    start_time = time.time()

    # Wait for the play button to be clickable and click it
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.ytp-play-button'))
    ).click()

    # Get the duration of the video
    duration = driver.execute_script('return document.querySelector(".ytp-time-duration").textContent')
    duration_parts = duration.split(':')
    # Convert minutes:seconds to seconds
    duration_seconds = int(duration_parts[-2]) * 60 + int(duration_parts[-1])

    print(f"Video duration: {duration_seconds} seconds")

    # Wait for the video to finish playing
    time.sleep(duration_seconds)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

# Total time taken
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")