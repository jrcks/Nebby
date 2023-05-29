# First time you will have to login manually 

# file_name = "discord"
with open("helper.py") as infile:
    exec(infile.read())

driver.get("https://discord.com/login")
wait = WebDriverWait(driver, 60)
time.sleep(2)
email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='email']")))
email.send_keys("client.ferb@gmail.com")
time.sleep(2)
psd = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
psd.send_keys("Ferb@Client@2000")
save_har_file(file_name+str(count))
count+=1

psd.send_keys(Keys.ENTER)
time.sleep(5)

driver.get("https://discord.com/channels/707230275175841915/956567494766764072")
time.sleep(10)

listen_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[div[text()='Listen In']]")))
listen_button.click()
time.sleep(30)

save_har_file(file_name+str(count))
count+=1


convert_to_one_har(file_name, count)

quit_driver()
