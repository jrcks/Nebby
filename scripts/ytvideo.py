from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
driver.get('https://www.youtube.com/watch?v=XALBGkjkUPQ')
# put the youtube video link here

# Wait for the video to load and play
start_time = time.time()

play_button = driver.find_element(By.CSS_SELECTOR, '.ytp-play-button')
play_button.click()

duration = driver.execute_script('return document.querySelector(".ytp-time-duration").textContent')
duration = duration.split(':')
duration_seconds = int(duration[-1]) + int(duration[-2]) * 60
print(duration_seconds) 


# Way 1
time.sleep(duration_seconds)

# Way 2 with error 

# # find the video element
# video = driver.find_element(By.CSS_SELECTOR, 'video')

# # # wait for the video to start playing
# # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'video[src][duration][currentTime]')))

# # wait for the video to finish playing
# duration = video.get_attribute('duration')
# WebDriverWait(driver, int(duration)).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'video[src][currentTime="' + str(duration) + '"]')))

end_time = time.time()

print(end_time - start_time)
driver.quit()
