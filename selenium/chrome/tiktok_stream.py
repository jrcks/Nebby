# file_name = "tiktok_stream"
with open("helper.py") as infile:
    exec(infile.read())

# Put the stream link here
driver.get('https://www.tiktok.com/@geturhits888/live')
time.sleep(30)


save_har_file(file_name)
quit_driver()