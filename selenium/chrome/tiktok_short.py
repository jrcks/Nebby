# file_name = "tiktok_short"

with open("helper.py") as infile:
    exec(infile.read())
try :

    # Put the short link here
    driver.get('[your_tiktok_short_link_here]')

    # wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='modal-close-inner-button']"))).click()

    time.sleep(30)

except Exception as e :
    print("Exceptions Raised for this : ", file_name , e)
    print()
finally :
    save_har_file(file_name)
    quit_driver()
