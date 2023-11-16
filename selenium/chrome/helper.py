# You will have to setup file_name from before in every file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import sys
import os
import json
file_name = sys.argv[1]
options = Options()
# options.add_argument('--headless')
logs_dir = os.path.dirname(os.path.dirname(os.getcwd())) + "/logs/"
options.add_argument("--log-net-log="+logs_dir +file_name+".json")
# options.add_argument('--ignore-certificate-errors')
options.add_argument("--auto-open-devtools-for-tabs")
options.add_argument("--autoplay-policy=no-user-gesture-required")
options.add_argument("--disable-extensions-except=../har-export-trigger-0.6.0")
options.add_argument("--load-extension=../har-export-trigger-master-0.6.0")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-notifications")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_argument("--enable-quic")
driver = webdriver.Chrome(options=options)

time.sleep(2)

# We wait ten minutes
wait = WebDriverWait(driver, 6000) 

har_harvest = """
myString = HAR.triggerExport().then(harLog => {
return JSON.stringify(harLog);
});
return myString
"""
def save_har_file(file_name):
    f = open(logs_dir + file_name + ".har","+w")
    f.write('{ "log" : ')
    f.write(driver.execute_script(har_harvest))
    f.write("}")
    f.close()

def convert_to_one_har(file_name, count):
    if count == 0:
        save_har_file(file_name)
    else :
        new_har_data = []
        for num in range(1,count+1):
            temp_har_data = json.load(open(logs_dir + file_name + str(num) + ".har"))
            new_har_data += temp_har_data['log']['entries']
        har_data = json.load(open(logs_dir + file_name + "1" + ".har"))
        har_data['log']['entries'] = new_har_data
        f = open(logs_dir + file_name + ".har","+w")
        json.dump(har_data,f)
        f.close()

def quit_driver():
    time.sleep(2)
    print("Quitting")
    driver.quit()
