# Using firefox 
# There is a non-trivial problem with Zoom not allowing request until it is made by a user mouse click
# There is a hack but it is not trusted : https://stackoverflow.com/questions/70089608/error-401-while-using-selenium-and-python-to-log-into-zoom-on-raspberry-pi
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

options = Options()
# options.add_argument('-headless')
options.set_preference("gfx.webrender.all", False)
options.set_preference('extensions.enabled', False)
options.set_preference('dom.webnotifications.enabled', False)
options.set_preference("dom.popup_maximum", 0)
options.set_preference("network.automatic-ntlm-auth.trusted-uris", "localhost")
options.set_preference("media.eme.enabled", True)
options.set_preference("media.gmp-manager.updateEnabled", True)
options.set_preference("privacy.trackingprotection.enabled", False)
options.add_argument("--disable-blink-features=AutomationControlled")
# options.set_preference("-profile", "/home/lakshayr/nus intern/test_profile")
# options.set_preference('media.gmp-widevinecdm.enabled', True)
# options.set_preference('media.gmp-widevinecdm.version', '1.4.8.1008')
# options.set_preference('media.gmp-widevinecdm.path', '/opt/google/chrome/WidevineCdm/_platform_specific/linux_x64/libwidevinecdm.so')

# Add links to gecko driver and firefox binary
from selenium.webdriver.firefox.service import Service
options.binary_location = "/opt/firefox/firefox"
driverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')
driver = webdriver.Firefox(options=options, service=driverService)
time.sleep(5)

driver.get('https://www.zoom.us/signin#/login')

wait = WebDriverWait(driver, 300) #Wait 5 Minutes

wait.until(EC.presence_of_element_located((By.XPATH,"//div[@id='onetrust-close-btn-container']/button"))).click()
time.sleep(2)
wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Sign in with Google']"))).click()
email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='identifier']")))
email.send_keys("client.ferb@gmail.com")
time.sleep(2)
email.send_keys(Keys.ENTER)
time.sleep(5)
psd = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='Passwd']")))
psd.send_keys("Ferb@Client@2000")
time.sleep(2)
psd.send_keys(Keys.ENTER)
time.sleep(10)

driver.get("https://us05web.zoom.us/meeting/schedule")

# start_time = wait.until(EC.presence_of_element_located(By.XPATH, "//div[@class='zm']"))
# might need to add scrolling option
passcode = wait.until(EC.presence_of_element_located((By.ID, "passcode")))
passcode.clear()
time.sleep(2)
passcode.send_keys("abcdef")

start_element = driver.find_element(By.XPATH, "//div[@class='zm-select mgl-sm start-time zm-select--small']/div/div/div/div/input")
start_time = start_element.get_attribute("aria-labels")
print(start_time)

driver.find_element(By.XPATH, "//div[@class='zm-sticky-fixed schedule-bar-sticky']/div/button[@class='zm-button--primary zm-button--small zm-button']").click()
time.sleep(5)

invite_link_element = driver.find_element(By.XPATH, "//div[@id='registration']/a")
invite_link = invite_link_element.get_attribute("href")
print(invite_link)

time.sleep(10)

driver.quit()