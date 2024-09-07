cc=$1
SCRIPT="./compile_server.sh; ./server 1 index.html ${cc}"
echo "In the Script to RUN the SERVER"
sshpass -p {SERVER_PASSWORD] ssh [IP_SERVER] "${SCRIPT}"
