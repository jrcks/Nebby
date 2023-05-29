# file_name = "youtube_video"
with open("helper.py") as infile:
    exec(infile.read())

driver.get('https://www.youtube.com/watch?v=XALBGkjkUPQ')

time.sleep(45)

save_har_file(file_name)

quit_driver()