cc=$1
SCRIPT="./compile_server.sh; ./server 1 index.html ${cc}"
echo "In the Script to RUN the SERVER"
sshpass -p 'lakshay123' ssh lakshay@edith.d2.comp.nus.edu.sg "${SCRIPT}"