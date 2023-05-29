# file_name = "tiktok_short"

with open("helper.py") as infile:
    exec(infile.read())

time.sleep(2)

# Put the short link here
driver.get('')

time.sleep(30)

save_har_file(file_name)
quit_driver()