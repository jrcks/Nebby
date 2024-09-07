
with open("helper.py") as infile:
    exec(infile.read())


driver.get('https://accounts.google.com')

count=0
email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='identifier']")))
email.send_keys("[your_gmail1_here]")
email.send_keys(Keys.ENTER)
time.sleep(5)
psd = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='Passwd']")))
psd.send_keys("[your_gmail_password1_here]")

count += 1
save_har_file(file_name+str(count))
psd.send_keys(Keys.ENTER)

time.sleep(5)

driver.get("https://meet.google.com")

print("Get Meet")

wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='iOSzxe']/div[@jsname='JXzze']/div[@jsname='WjL7X']/div/button"))).click()

count += 1
save_har_file(file_name+str(count))

wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='iOSzxe']/div[@jsname='JXzze']/div[@jsname='U0exHf']/div/ul[@role='menu']/li[@aria-label='Start an instant meeting']"))).click()

link = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='xTGfdf']/div[@class='cuAK0d']/div[@class='gvnMbb']/div")))


count += 1
save_har_file(file_name+str(count))

print(link.text)


def foo(file_name, count):
    # childDriverService = Service('/home/lakshayr/nus intern/geckodriver-v0.32.0-linux64/geckodriver')
    child_driver = webdriver.Chrome(options=options)
    # child_driver.switch_to.new_window('window')
    # child_driver = webdriver.Firefox(options=options, service=driverService)

    child_driver.get('https://accounts.google.com')

    child_wait = WebDriverWait(child_driver, 300) #Wait 5 Minutes

    child_email = child_wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='identifier']")))
    print("Reached")
    child_email.send_keys("[your_gmail2_here]")
    child_email.send_keys(Keys.ENTER)
    time.sleep(5)
    child_psd = child_wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='Passwd']")))
    child_psd.send_keys("[your_gmail_password2_here]")
    child_psd.send_keys(Keys.ENTER)
    time.sleep(5)
    child_driver.get("https://meet.google.com")
    link_input = child_wait.until(EC.presence_of_element_located((By.XPATH,"//input[@aria-label='Enter a code or link']")))
    link_input.send_keys(link.text)
    link_input.send_keys(Keys.ENTER)
    time.sleep(5)
    print("Joining")
    child_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Ask to join']]"))).click()
    time.sleep(120)
    child_driver.quit()

import threading
child_client = threading.Thread(target=foo,args=(file_name, count))
child_client.start()
print("Started Child")

time.sleep(30)

wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Got it']]"))).click()
wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-mdc-dialog-action='accept']"))).click()

time.sleep(15)
count += 1
save_har_file(file_name+str(count))

convert_to_one_har(file_name, count)

quit_driver()
