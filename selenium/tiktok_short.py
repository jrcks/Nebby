### Working

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

options = Options()

options.add_argument('-headless')

# enable auto play
options.set_preference("media.autoplay.default", 0)

options.add_argument('-headless')

options.set_preference("gfx.webrender.all", False) # If true improves the rendering process in the browser

options.set_preference('dom.webnotifications.enabled', False) # We don't want notifications posing any problems while accessing web pages

options.set_preference("dom.popup_maximum", 0) # We dont want any pop ups

options.set_preference("media.eme.enabled", True) # Enable Playing DRM content, if False asks for permission
options.set_preference("media.gmp-manager.updateEnabled", True) # Enables automatic updating for this


from selenium.webdriver.firefox.service import Service
options.binary_location = "/opt/firefox/firefox"
driverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')

driver = webdriver.Firefox(options=options, service=driverService)


# ask for web3 to work
options.set_preference("network.http.http3.enable",True)
options.set_preference("network.http.http3.alt-svc-mapping-for-testing", 'https://www.tiktok.com/;h3:":443";h3-29=":443"')

driver.get("https://www.tiktok.com/")
time.sleep(10)

driver.get('https://www.tiktok.com/@vitaminnchill/video/7227343734734687531') # 10 Second
# driver.get('https://www.tiktok.com/@lil.murks/video/7206431137370033414') # 1 minute video

time.sleep(20)

driver.quit()