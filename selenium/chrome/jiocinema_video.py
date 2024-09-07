# First start the VPN to India
# This is to run a video
# Try to use the profile specified, otherwise preferences for autoplay will have to be set manually 
# file_name = "jiocinema"
with open("helper.py") as infile:
    exec(infile.read())
try : 
    driver.get("https://www.jiocinema.com/")
    time.sleep(10)
    driver.get('[your_video_link_here]')
    time.sleep(100)

except Exception as e :
    print("Exceptions Raised for this : ", file_name , e)
    print()

finally :
    save_har_file(file_name)
    quit_driver()
