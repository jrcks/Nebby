# Using firefox 
# Sets one client, 
# Working for setting two clients
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
options.set_preference("media.eme.enabled", True)
options.set_preference("media.gmp-manager.updateEnabled", True)
options.add_argument("-private")
#key flag
options.set_preference("privacy.trackingprotection.enabled", False)

#for allowing use of audio and video
options.set_preference('media.navigator.permission.disabled', True)
options.set_preference('media.navigator.streams.fake', True)
options.set_preference('media.getusermedia.browser.enabled', True)
options.set_preference('media.getusermedia.screensharing.enabled', True)

# ask for web3 to work
options.set_preference("network.http.http3.enable", True)
options.set_preference("network.http.http3.alt-svc-mapping-for-testing", 'https://meet.google.com/;h3:":443";h3-29=":443"')

# Add links to gecko driver  and firefox binary

from selenium.webdriver.firefox.service import Service
options.binary_location = "/opt/firefox/firefox"
driverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')

driver = webdriver.Firefox(options=options, service=driverService)

driver.get('https://accounts.google.com')

wait = WebDriverWait(driver, 300) #Wait 5 Minutes


email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='identifier']")))
email.send_keys("client.ferb@gmail.com")
email.send_keys(Keys.ENTER)
time.sleep(5)
psd = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='Passwd']")))
psd.send_keys("Ferb@Client@2000")
psd.send_keys(Keys.ENTER)
time.sleep(5)

driver.get("https://meet.google.com")

print("Get Meet")

wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='iOSzxe']/div[@jsname='JXzze']/div[@jsname='WjL7X']/div/button"))).click()

wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='iOSzxe']/div[@jsname='JXzze']/div[@jsname='U0exHf']/div/ul[@role='menu']/li[@aria-label='Start an instant meeting']"))).click()

link = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='xTGfdf']/div[@class='cuAK0d']/div[@class='gvnMbb']/div")))

print(link.text)

def foo():
    # childDriverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')
    child_driver = driver
    child_driver.switch_to.new_window('window')
    # child_driver = webdriver.Firefox(options=options, service=driverService)

    child_driver.get('https://accounts.google.com')

    child_wait = WebDriverWait(child_driver, 300) #Wait 5 Minutes

    child_email = child_wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='identifier']")))
    print("Reached")
    child_email.send_keys("uselessemail3105@gmail.com")
    child_email.send_keys(Keys.ENTER)
    time.sleep(5)
    child_psd = child_wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='Passwd']")))
    child_psd.send_keys("donotusethisemail")
    child_psd.send_keys(Keys.ENTER)
    time.sleep(5)
    child_driver.get("https://meet.google.com")
    link_input = child_wait.until(EC.presence_of_element_located((By.XPATH,"//input[@aria-label='Enter a code or link']")))
    link_input.send_keys(link.text)
    link_input.send_keys(Keys.ENTER)
    time.sleep(60)
    child_driver.quit()

import threading
child_client = threading.Thread(target=foo)
child_client.start()
print("Started Child")
time.sleep(120)

driver.quit()