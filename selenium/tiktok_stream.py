### Working
 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import time

options = Options()

options.add_argument('-headless')

# enable auto play
options.set_preference("media.autoplay.default", 0)
options.set_preference("gfx.webrender.all", False)
options.set_preference('extensions.enabled', False)

options.set_preference('dom.webnotifications.enabled', False)

options.set_preference("dom.popup_maximum", 0)

options.set_preference("media.eme.enabled", True)
options.set_preference("media.gmp-manager.updateEnabled", True)

# ask for web3 to work
options.set_preference("network.http.http3.enable",True)
options.set_preference("network.http.http3.alt-svc-mapping-for-testing", 'https://www.tiktok.com/;h3:":443";h3-29=":443"')


from selenium.webdriver.firefox.service import Service
options.binary_location = "/opt/firefox/firefox"
driverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')

driver = webdriver.Firefox(options=options, service=driverService)

driver.get("https://www.tiktok.com/")

# Put the stream link here
driver.get('https://www.tiktok.com/@geturhits888/live')

time.sleep(20)

driver.quit()