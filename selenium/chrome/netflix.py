
# file_name = "netflix"
with open("helper.py") as infile:
    exec(infile.read())
count = 0

try :
    driver.get('https://www.netflix.com/login') 

    user_id = wait.until(EC.presence_of_element_located((By.NAME, 'userLoginId')))
    user_id.send_keys("[your_netflix_id_here]")
    password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    password.send_keys('[your_netflix_password_here]')
    time.sleep(5)
    count += 1
    save_har_file(file_name+str(count))

    driver.find_element(By.CSS_SELECTOR,'.login-button').click()
    time.sleep(5)

    driver.get("https://www.netflix.com/")
    time.sleep(5)

    count+=1
    save_har_file(file_name+str(count))


    driver.get("[your_netflix_video_link_here]")
    time.sleep(120)
    count+=1
    save_har_file(file_name+str(count))
    
except Exception as e :
    print("Exceptions Raised for this : ", file_name , e)
    print()

finally:
    convert_to_one_har(file_name, count)

    quit_driver()
