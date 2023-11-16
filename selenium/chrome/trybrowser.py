# First time you will have to login manually 

# file_name = "discord"
import sys

url=str(sys.argv[1])

with open("helper.py") as infile:
    exec(infile.read())
count=0

try : 
    driver.get(url)
    time.sleep(30)
    
except Exception as e :
    print("Exceptions Raised for this : ", file_name , e)
    print()

finally :
    convert_to_one_har(file_name, count)
    quit_driver()
