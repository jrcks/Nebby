# First start the VPN to India
# This is to run a video
# Try to use the profile specified, otherwise preferences for autoplay will have to be set manually 
# file_name = "jiocinema"
with open("helper.py") as infile:
    exec(infile.read())

driver.get("https://www.jiocinema.com/")
time.sleep(10)
driver.get('https://www.jiocinema.com/sports/gt-vs-dc-highlights/3739293')
time.sleep(100)

save_har_file(file_name)
quit_driver()