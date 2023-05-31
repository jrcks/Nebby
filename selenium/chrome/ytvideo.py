# file_name = "youtube_video"
with open("helper.py") as infile:
    exec(infile.read())

try :
    driver.get('https://www.youtube.com/watch?v=XALBGkjkUPQ')

    time.sleep(45)


except Exception as e :
    print("Exceptions Raised for this : ", file_name , e)
    print()

finally:
    save_har_file(file_name)

    quit_driver()