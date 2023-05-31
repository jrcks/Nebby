# file_name = "twitchvideo"

with open("helper.py") as infile:
    exec(infile.read())

try:
#viedo URL goes here:
    video_url="https://www.twitch.tv/esl_csgo" #sys.argv[1]
    driver.get(video_url)

# Wait for the video to load and play
    time.sleep(60)

except Exception as e:
    print("Exceptions Raised for this : ", file_name , e)
    print()
    
finally:
    save_har_file(file_name)
    quit_driver()