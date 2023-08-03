#include <stdio.h>
#include <unistd.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <errno.h>
#include <pthread.h>
#include <sys/wait.h>
#define PORT 8083
#define BUFFSIZE 150 * 1024
#define SA struct sockaddr
   

// Function to run the script that runs the custom client on the remote server
void* run_client(void* arg){
    char* cc = (char*) arg;
    char comm[25] = "./run_custom_server.sh ";
    strcat(comm, cc);
    system(comm);
    pthread_exit(NULL);
    return NULL;
}
// Function designed for chat between client and server.
void func(int connfd, int flow_size, char* fname)
{   
    char buff[flow_size];
    bzero(buff,flow_size);
    //Set TCP_QUICKACK each read
    int on = 1;
    if(setsockopt( connfd, IPPROTO_TCP, TCP_QUICKACK, (void *)&on, sizeof(on))==-1){
        perror("TCP_QUICKACK failure");
        exit(-1);
    }

    int bytes_recv = 0;
    while(1){
        int num_bytes  = recv(connfd, buff + bytes_recv, BUFFSIZE, 0);
        if(num_bytes == -1){
            perror("Receive Failes");
            exit(EXIT_FAILURE);
        } 
        else if (num_bytes == 0){
            break;
        }
        bytes_recv += num_bytes;
        // printf("Received Bytes %d\n", num_bytes);
        // fflush(stdout);
    }
    char new_file[] = "new.html";
    FILE* fp = fopen(new_file, "w+");
    fwrite(buff, 1, sizeof(buff), fp);
    fclose(fp);
    printf("Total Bytes Received %d\n", bytes_recv);
    fflush(stdout);
}
   
// Driver function
int main(int argc, char *argv[])
{
    int sockfd, connfd;
    char fname[256];
    socklen_t len;
    struct sockaddr_in servaddr, cli;

    int flow_size, num_flow;
    char congestion_ctl[256];
    struct linger so_linger;

    char* str_ptr;

    if(argc == 1)
        num_flow = 100;
    else
        num_flow = (int)(atoi(argv[1])); 
    
    if(num_flow == 0)
        printf("Error: please enter a valid value for the number of flows");
    
    if(argc < 3)
        flow_size = 80 * 1024;
    else {
    	FILE* fp = fopen(argv[2], "r");
        fseek(fp,0L,SEEK_END);
        int sz = ftell(fp);
        printf("Size of File %d", sz);
        fflush(stdout);
        flow_size = sz;
        strcpy(fname, argv[2]);
        fclose(fp); 
    }
    if( flow_size == 0)
        printf("Error: please enter a valid value for flow size");

    if(argc < 4)
        strcpy(congestion_ctl, "cubic");
    else
        strcpy(congestion_ctl, argv[3]);

    printf("Flow size is %d, congestion control algorithm is %s \n",flow_size,congestion_ctl);
    


    // socket create and verification
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        printf("socket creation failed...\n");
        exit(0);
    }
    else
        printf("Socket successfully created..\n");
    bzero(&servaddr, sizeof(servaddr));
   
    // assign IP, PORT
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(PORT);
   
    // Binding newly created socket to given IP and verification
    if ((bind(sockfd, (SA*)&servaddr, sizeof(servaddr))) != 0) {
        printf("socket bind failed...\n");
        exit(0);
    }
    else
        printf("Socket successfully binded..\n");

    // Now server is ready to listen and verification
    if ((listen(sockfd, 5)) != 0) {
        printf("Listen failed...\n");
        exit(0);
    }
    else
        printf("Server listening..\n");
    len = sizeof(cli);
    // pthread_t thread;
    // if(pthread_create(&thread, NULL, run_client, (char *)congestion_ctl)!=0){
    //     fprintf(stderr, "Failed to create thread\n");
    //     return 1;
    // }
    // pid_t pid = fork();
    // if(pid==-1){
    //     fprintf(stderr, "Failed to create process\n");
    //     return 1;
    // }
    // else if (pid==0){
    //     printf("Starting the process that runs the server  #########\n");
    //     run_client((char *)congestion_ctl);
    // }
    for(int i = 0; i < num_flow ; i++){
        // Accept the data packet from client and verification
        connfd = accept(sockfd, (SA*)&cli, &len);
        if (connfd < 0) {
            perror("server accept failed...\n");
            exit(0);
        }
        else
            printf("# %d server accept the client...\n", i + 1);

        //Set TCP_NODELAY each connection
        int on = 1;
        if(setsockopt( connfd, IPPROTO_TCP, TCP_NODELAY, (void *)&on, sizeof(on)) == -1){
            perror("TCP_NODELAY failure");
            return -1;
        }    

        //Clear TCP_CORK each connection
        int off = 0;
        if(setsockopt(connfd, IPPROTO_TCP, TCP_CORK, (void *)&off, sizeof(off)) == -1){
            perror("TCP_CORK failure");
            return -1;
        }

        //Set recv buffer size
        int size = BUFFSIZE;
        if(setsockopt(connfd, SOL_SOCKET, SO_RCVBUFFORCE, &size, sizeof(size)) == -1){
            perror("RCVBUF failure");
            return -1;
        }

        // Set congestion control algorithm
        if(setsockopt(connfd, IPPROTO_TCP, TCP_CONGESTION, (char *)congestion_ctl, sizeof(congestion_ctl))!=0){
            perror("congestion contorl algorithm specification error on the receiver!");
            return -1;
        }

        // Set SO_LINGER
        so_linger.l_onoff = 1;
        so_linger.l_linger = 30;
        if(setsockopt(connfd,SOL_SOCKET,SO_LINGER,&so_linger,sizeof so_linger)!= 0){
            perror("SO_LINGER failure on the receiver!");
            return -1;
        }

        // Function for chatting between client and server
        func(connfd,flow_size,fname);

        //shutdown(connfd, SHUT_WR);
        close(connfd);
        
   }
//    if (pthread_join(thread, NULL) != 0){
//     fprintf(stderr, "Failed to join the thread\n");
//     return 1;
//    }
    // After chatting close the socket
    shutdown(sockfd, SHUT_WR);
}
