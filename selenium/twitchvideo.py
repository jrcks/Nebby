from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import sys

options = Options()
#launch in headless mode
#options.add_argument('--headless')

driver = webdriver.Chrome(options=options)

#viedo URL goes here:
video_url="https://www.twitch.tv/esl_csgo" #sys.argv[1]
driver.get(video_url)

# Wait for the video to load and play
start_time = time.time()

play_button = driver.find_element(By.CSS_SELECTOR, '.eWaZXT') #'.ScCoreButton-sc-ocjdkq-0'
play_button.click()

print("Twitch takes a long time to load on slow connections, manually terminate if it takes too long!")

#old code for getting yt video duration
#duration = driver.execute_script('return document.querySelector(".ytp-time-duration").textContent')
#duration = duration.split(':')
#duration_seconds = int(duration[-1]) + int(duration[-2]) * 60

#duration: wait for the client to load the video, stream it for a bit, etc.
duration_seconds=59
print(duration_seconds) 

# Way 1
time.sleep(duration_seconds)

end_time = time.time()

print(end_time - start_time)
driver.quit()
