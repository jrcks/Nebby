# First start the VPN to India
# This is to run a video
# Try to use the profile specified, otherwise preferences for autoplay will have to be set manually 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

options = Options()

options.add_argument('-headless')

# enable auto play
options.set_preference("media.autoplay.default", 0)
# options.add_argument('-headless')
options.set_preference("gfx.webrender.all", False)
options.set_preference('extensions.enabled', False)

options.set_preference('dom.webnotifications.enabled', False)
options.set_preference("dom.popup_maximum", 0)

options.set_preference("media.eme.enabled", True)
options.set_preference("media.gmp-manager.updateEnabled", True)
# ask for web3 to work
options.set_preference("network.http.http3.enable", True)
options.set_preference("network.http.http3.alt-svc-mapping-for-testing", 'https://www.jiocinema.com/;h3:":443";h3-29=":443"')

driver = webdriver.Firefox(options=options, executable_path="/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver", firefox_binary="/opt/firefox/firefox")
driver.get("https://www.jiocinema.com/")
time.sleep(10)
driver.get('https://www.jiocinema.com/sports/gt-vs-dc-highlights/3739293')
time.sleep(100)

driver.quit()