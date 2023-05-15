# Using firefox 
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
options.set_preference("network.http.phishy-userpass-length", 255)
options.set_preference("network.automatic-ntlm-auth.trusted-uris", "localhost")
options.set_preference("media.eme.enabled", True)
options.set_preference("media.gmp-manager.updateEnabled", True)
options.set_preference("privacy.trackingprotection.enabled", False)

#for allowing use of audio and video
options.set_preference('media.navigator.permission.disabled', True)
options.set_preference('media.navigator.streams.fake', True)
options.set_preference('media.getusermedia.browser.enabled', True)
options.set_preference('media.getusermedia.screensharing.enabled', True)
# ask for web3 to work
options.set_preference("network.http.http3.enable", True)
options.set_preference("network.http.http3.alt-svc-mapping-for-testing", 'https://discord.com/;h3:":443";h3-29=":443"')

from selenium.webdriver.firefox.service import Service
options.binary_location = "/opt/firefox/firefox"
driverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')

driver = webdriver.Firefox(options=options, service=driverService)

driver.get("https://discord.com/login")

wait = WebDriverWait(driver, 60)
time.sleep(2)
email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='email']")))
email.send_keys("client.ferb@gmail.com")
time.sleep(2)
psd = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
psd.send_keys("Ferb@Client@2000")
psd.send_keys(Keys.ENTER)
time.sleep(5)

driver.get("https://discord.com/channels/707230275175841915/956567494766764072")
time.sleep(10)
listen_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[div[text()='Listen In']]")))
listen_button.click()
time.sleep(30)

driver.quit()
