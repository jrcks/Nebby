# Ads present
# Works

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
# options.add_argument('-headless')
options.set_preference("gfx.webrender.all", False)
options.set_preference('extensions.enabled', False)
options.set_preference('dom.webnotifications.enabled', False)
options.set_preference("dom.popup_maximum", 0)
options.set_preference("media.eme.enabled", True)
options.set_preference("media.gmp-manager.updateEnabled", True)


# enable auto play
options.set_preference("media.autoplay.default", 0)

# ask for web3 to work
options.set_preference("network.http.http3.enable", True)
options.set_preference("network.http.http3.alt-svc-mapping-for-testing", 'https://music.youtube.com/;h3:":443";h3-29=":443"')

# Add links to gecko driver and firefox binary

from selenium.webdriver.firefox.service import Service
options.binary_location = "/opt/firefox/firefox"
driverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')

driver = webdriver.Firefox(options=options, service=driverService)

driver.get("https://music.youtube.com/")
time.sleep(10)

driver.get("https://music.youtube.com/watch?v=C-QtlXOp4Zo")
wait = WebDriverWait(driver,30)
# Add a check to see if an AD ran

try:
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[div[text()='Skip Ads']]"))).click()
    print("Clickable Ad Present")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='ytp-ad-skip-button ytp-button']"))).click()
    print("Clickable Ad Present")
    time.sleep(100)
    driver.quit()

except:
    print("Not detecting Ads now.")
    time.sleep(100)
    driver.quit()



