
# file_name = "netflix"
with open("helper.py") as infile:
    exec(infile.read())

driver.get('https://www.netflix.com/login') 

user_id = wait.until(EC.presence_of_element_located((By.NAME, 'userLoginId')))
user_id.send_keys("drpradeep_raj@yahoo.in")
password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
password.send_keys('Pradeep@1290')
time.sleep(5)
count = 1
save_har_file(file_name+str(count))
count+=1

driver.find_element(By.CSS_SELECTOR,'.login-button').click()
time.sleep(5)

driver.get("https://www.netflix.com/")
time.sleep(5)
save_har_file(file_name+str(count))
count+=1

driver.get("https://www.netflix.com/watch/81576597?trackId=253448517&tctx=1%2C0%2C265bedfb-7855-4be9-95d7-1ac8abd4c9df-141488113%2CNES_87386034059ACA445E74EE85300003-A64A86483F8E63-2E7DEF8CA1_p_1683023261679%2CNES_87386034059ACA445E74EE85300003_p_1683023261679%2C%2C%2C%2C81576597%2CVideo%3A81576597%2CminiDpPlayButton")
time.sleep(120)
save_har_file(file_name+str(count))
count+=1

convert_to_one_har(file_name, count)

quit_driver()