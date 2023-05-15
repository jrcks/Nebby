################## Set Login and Password ####################  
## WORKS ##
# Using firefox 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

options = Options()
options.add_argument('-headless') # Comment this if you want to debug
options.set_preference("gfx.webrender.all", False)
options.set_preference('extensions.enabled', False)

options.set_preference('dom.webnotifications.enabled', False)

options.set_preference("dom.popup_maximum", 0)

options.set_preference("media.eme.enabled", True) # Enable Playing DRM content, if False asks for permission
options.set_preference("media.gmp-manager.updateEnabled", True) # Enables automatic updating for this

# ask for web3 to work
options.set_preference("network.http.http3.enable",True)
options.set_preference("network.http.http3.alt-svc-mapping-for-testing", 'https://open.spotify.com;h3:":443";h3-29=":443"')

# Add links to gecko driver and firefox binary
from selenium.webdriver.firefox.service import Service
options.binary_location = "/opt/firefox/firefox"
driverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')

driver = webdriver.Firefox(options=options, service=driverService)

wait = WebDriverWait(driver, 300) #Wait 5 Minutes

driver.get('https://accounts.spotify.com/en/login')
wait.until(EC.presence_of_element_located((By.ID,'login-button'))) #put in tuple

driver.find_element(By.ID, 'login-username').send_keys('uselessemail3105@gmail.com')
driver.find_element(By.ID,'login-password').send_keys("Lakshay@31")
driver.find_element(By.ID, 'login-button').click()
print("logged in")

wait.until(EC.url_matches("https://accounts.spotify.com/en/status"))

driver.get("https://open.spotify.com/track/3hts3cIWNG8A2063si9GLP")
# driver.get("https://open.spotify.com/search/hey%20ya")

print("Fetched Song")

close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='onetrust-banner-sdk']/div/div[@id='onetrust-close-btn-container']/button"))).click()
wait.until(EC.presence_of_element_located((By.XPATH, "//a[@data-testid='context-item-link']")))

print("DRM Downloaded")

play_button = wait.until(EC.presence_of_element_located((By.XPATH,"//div[@data-testid='action-bar-row']/div/button[@data-testid='play-button']"))).click()
print("Played")

time.sleep(200)

driver.quit()
