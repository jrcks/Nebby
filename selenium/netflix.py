# Add username password
# Working
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time

options = Options()

# Uncomment this line to run headless
options.add_argument('-headless')
options.set_preference("gfx.webrender.all", False)

options.set_preference('extensions.enabled', False)

options.set_preference('dom.webnotifications.enabled', False)

options.set_preference("dom.popup_maximum", 0)

options.set_preference("media.eme.enabled", True)
options.set_preference("media.gmp-manager.updateEnabled", True)
options.set_preference("media.autoplay.default", 0)

# ask for web3 to work
options.set_preference("network.http.http3.enable", True)
options.set_preference("network.http.http3.alt-svc-mapping-for-testing", 'https://www.netflix.com/;h3:":443";h3-29=":443"')


from selenium.webdriver.firefox.service import Service
options.binary_location = "/opt/firefox/firefox"
driverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')

driver = webdriver.Firefox(options=options, service=driverService)

wait = WebDriverWait(driver, 300)

driver.get('https://www.netflix.com/login') 

user_id = wait.until(EC.presence_of_element_located((By.NAME, 'userLoginId')))
user_id.send_keys("username")
password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
password.send_keys('password')
time.sleep(5)

driver.find_element(By.CSS_SELECTOR,'.login-button').click()
time.sleep(5)

driver.get("https://www.netflix.com/")
time.sleep(5)

driver.get("https://www.netflix.com/watch/81576597?trackId=253448517&tctx=1%2C0%2C265bedfb-7855-4be9-95d7-1ac8abd4c9df-141488113%2CNES_87386034059ACA445E74EE85300003-A64A86483F8E63-2E7DEF8CA1_p_1683023261679%2CNES_87386034059ACA445E74EE85300003_p_1683023261679%2C%2C%2C%2C81576597%2CVideo%3A81576597%2CminiDpPlayButton")
time.sleep(5)

time.sleep(120)
driver.quit()
