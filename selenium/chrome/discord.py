# First time you will have to login manually 

# file_name = "discord"
with open("helper.py") as infile:
    exec(infile.read())
count=0

try : 
    driver.get("https://discord.com/login")
    time.sleep(2)
    email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='email']")))
    email.send_keys("[your_email_here]")
    time.sleep(2)
    psd = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
    psd.send_keys("[your_password_here]")

    count+=1
    save_har_file(file_name+str(count))

    psd.send_keys(Keys.ENTER)
    time.sleep(5)

    driver.get("[your_channel_here]")
    time.sleep(10)

    listen_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[div[text()='Listen In']]")))
    listen_button.click()
    time.sleep(30)
    count+=1
    save_har_file(file_name+str(count))
    
except Exception as e :
    print("Exceptions Raised for this : ", file_name , e)
    print()

finally :
    convert_to_one_har(file_name, count)
    quit_driver()
