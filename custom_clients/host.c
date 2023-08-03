#include <netdb.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <errno.h>
#include <time.h>
#include <errno.h>
#include <pthread.h>
#include <sys/wait.h>
#define PORT 8080   
#define BUFFSIZE 150 * 1024
#define RECORD_PERIOD 50000
#define BASEFILENAME "stats.csv"
#define SA struct sockaddr
#define DEST_IP "18.142.186.24"
#define SRC_IP "100.111.111.31"


void* run_server(void* arg){
    char* cc = (char*) arg;
    char comm[25] = "./_run_custom_server.sh ";
    strcat(comm, cc);
    system(comm);
    printf("Reached\n");
    fflush(stdout);
    pthread_exit(NULL);
}
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
   
int main(int argc, char *argv[])
{   
    // printf("%d\n", argc);
    // printf("%d\n", argc);
    printf("%s\n",DEST_IP);
    fflush(stdout);
    int sockfd;
    char fname[256];
    socklen_t len;
    struct sockaddr_in servaddr, cli;

    int flow_size, num_flow;
    char congestion_ctl[256];
    struct linger so_linger;

    char* str_ptr;

    pthread_t thread;

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
        printf("Size of File %d\n", sz);
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
    
    // if(pthread_create(&thread, NULL, run_server,(char*) congestion_ctl)!=0){
    //     perror("Could not creat Thread to Run Server");
    //     return 1;
    // }
    // socket create and varification
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        printf("socket creation failed...\n");
        exit(0);
    }

    bzero(&servaddr, sizeof(servaddr));
    bzero(&cli, sizeof(cli));
    
    // assign IP, PORT
    cli.sin_family = AF_INET;
    cli.sin_addr.s_addr = inet_addr(SRC_IP);
    cli.sin_port = htons(33117);

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr(DEST_IP);
    servaddr.sin_port = htons(PORT);


    //Set TCP_NODELAY each connection
    int on = 1;
    if(setsockopt( sockfd, IPPROTO_TCP, TCP_NODELAY, (void *)&on, sizeof(on)) == -1){
        perror("TCP_NODELAY failure");
        return -1;
    }    

    //Clear TCP_CORK each connection
    int off = 0;
    if(setsockopt(sockfd, IPPROTO_TCP, TCP_CORK, (void *)&off, sizeof(off)) == -1){
        perror("TCP_CORK failure");
        return -1;
    }

    //Set recv buffer size
    int size = BUFFSIZE;
    if(setsockopt(sockfd, SOL_SOCKET, SO_RCVBUFFORCE, &size, sizeof(size)) == -1){
        perror("RCVBUF failure");
        return -1;
    }

    // set max seg size
    // int max_seg_size = 100;
    // if(setsockopt( sockfd, IPPROTO_TCP, TCP_MAXSEG, (void *)&max_seg_size, sizeof(max_seg_size))!=0){
    //     perror("MSS Error\n");
    //     return -1;
    // }  

    // Set congestion control algorithm
    if(setsockopt(sockfd, IPPROTO_TCP, TCP_CONGESTION, (char *)congestion_ctl, sizeof(congestion_ctl))!=0){
        perror("congestion contorl algorithm specification error on the receiver!");
        return -1;
    }

    // Set SO_LINGER
    so_linger.l_onoff = 1;
    so_linger.l_linger = 30;
    if(setsockopt(sockfd,SOL_SOCKET,SO_LINGER,&so_linger,sizeof so_linger)!= 0){
        perror("SO_LINGER failure on the receiver!");
        return -1;
    }
    
    // Bind Socket
    // if ((bind(sockfd, (SA*)&cli, sizeof(cli))) != 0) {
    //     printf("socket bind failed for client...\n");
    //     printf("%s\n", strerror(errno));
    //     fflush(stdout);
    //     fflush(stderr);
    //     return -1;
    //     // exit(0);
    // }
    // connect the client socket to server socket
    if (connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
        printf("connection with the server failed...\n");
        printf("%s\n", strerror(errno));
        fflush(stdout);
        fflush(stderr);
        exit(0);
    }

    func(sockfd,flow_size,fname);
    close(sockfd);
    // pthread_join(thread, NULL);

    // After chatting close the socket
    shutdown(sockfd, SHUT_WR);

}
