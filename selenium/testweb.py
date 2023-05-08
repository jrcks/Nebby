from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import sys

options = Options()
#launch in headless mode
#options.add_argument('--headless')

driver = webdriver.Chrome(options=options)

#web URL goes here:
print("fetching URL")
#web_url="https://www.reddit.com/r/AskReddit/comments/brlti4/reddit_what_are_some_underrated_apps/" #sys.argv[1]
web_url="https://www.youtube.com/"
driver.get(web_url)
print("webpage completely fetched!")

driver.quit()
