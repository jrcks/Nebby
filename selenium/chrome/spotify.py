

with open("helper.py") as infile:
    exec(infile.read())
count = 0

try :
    driver.get('https://accounts.spotify.com/en/login')
    wait.until(EC.presence_of_element_located((By.ID,'login-button'))) #put in tuple

    driver.find_element(By.ID, 'login-username').send_keys('uselessemail3105@gmail.com')
    driver.find_element(By.ID,'login-password').send_keys("Lakshay@31")

    count += 1
    save_har_file(file_name+str(count))

    driver.find_element(By.ID, 'login-button').click()
    print("Logged In")

    wait.until(EC.url_matches("https://accounts.spotify.com/en/status"))

    count+=1
    save_har_file(file_name+str(count))


    # driver.get("https://open.spotify.com/track/3hts3cIWNG8A2063si9GLP")
    driver.get("https://open.spotify.com/track/1qTh7hzjd361hjuzeaMFWK")

    print("Fetched Song")

    close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='onetrust-banner-sdk']/div/div[@id='onetrust-close-btn-container']/button"))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@data-testid='context-item-link']")))

    print("DRM Downloaded")

    play_button = wait.until(EC.presence_of_element_located((By.XPATH,"//div[@data-testid='action-bar-row']/div/button[@data-testid='play-button']"))).click()
    print("Played")

    time.sleep(30)
    count+=1
    save_har_file(file_name+str(count))

except Exception as e :
    print("Exceptions Raised for this : ", file_name , e)
    print()

finally:
    convert_to_one_har(file_name, count)

    quit_driver()