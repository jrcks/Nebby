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
#define BUFFSIZE 150 * 1024
#define SA struct sockaddr
   
// Function designed for chat between client and server.
void func(int connfd, int flow_size)
{   
    int total_size = 0;
    int size = 0;
    while(1){
        char buff[flow_size];

        bzero(buff,flow_size);
        //Set TCP_QUICKACK each read
        int on = 1;
        if(setsockopt( connfd, IPPROTO_TCP, TCP_QUICKACK, (void *)&on, sizeof(on))==-1){
            perror("TCP_QUICKACK failure");
            exit(-1);
        }

        if(total_size < flow_size)
            size =  recv(connfd, buff, flow_size + 1,MSG_DONTWAIT); //non-blocking
        else
            size =  recv(connfd, buff, flow_size + 1,0);// blocking
        
        if(size > 0){
            total_size += size;
            if (total_size == flow_size){
                printf("The size received is %d B\n",total_size);
                break;
            }
        }
        else if(size == 0 && total_size >= flow_size)
            break;
    }

}
   
// Driver function
int main(int argc, char *argv[])
{
    int sockfd, connfd;
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
    
    if( num_flow == 0)
        printf("Error: please enter a valid value for the number of flows");
    
    if(argc < 2)
        flow_size = 80 * 1024;
    else
        flow_size = (int)(atof(argv[2]) * 1024); 
    
    if( flow_size == 0)
        printf("Error: please enter a valid value for flow size");

    if(argc < 3)
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
    servaddr.sin_port = htons(8080);
   
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
        func(connfd,flow_size);

        //shutdown(connfd, SHUT_WR);
        close(connfd);
        
   }
    // After chatting close the socket
    shutdown(sockfd, SHUT_WR);
}