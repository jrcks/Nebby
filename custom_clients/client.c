#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <pthread.h>
#include <errno.h>

#define PORT 8080
#define DEST_IP "127.0.0.1"
#define BUFFSIZE (150 * 1024)
#define SA struct sockaddr

// Function to receive data from the server and store it in a file
void receive_data(int connfd, int flow_size)
{
    // Enable TCP_QUICKACK option every connection to reduce acknowledgment latency
    int on = 1;
    if (setsockopt(connfd, IPPROTO_TCP, TCP_QUICKACK, (void *)&on, sizeof(on)) == -1)
    {
        perror("TCP_QUICKACK Failure");
        exit(EXIT_FAILURE);
    }

    // Buffer to store received data
    char buff[flow_size];
    bzero(buff, flow_size);

    // Receive data from the server
    int bytes_recv = 0;
    while (1)
    {
        // Receive data from the server
        int num_bytes = recv(connfd, buff + bytes_recv, BUFFSIZE, 0);
        if (num_bytes == -1)
        {
            perror("Receive Failed");
            exit(EXIT_FAILURE);
        }
        else if (num_bytes == 0)
        {
            break; // Connection has been closed by the server
        }
        bytes_recv += num_bytes; // Update the total received byte count
    }

    // Store the received data into a file
    FILE *fp = fopen("new.html", "w+");
    if (fp == NULL)
    {
        perror("Error opening file for writing");
        exit(EXIT_FAILURE);
    }
    // Write the actual number of received bytes to the file
    fwrite(buff, 1, bytes_recv, fp);
    fclose(fp);

    // Log the total number of bytes received
    printf("Total Bytes Received: %d\n", bytes_recv);
}

// Function to check and parse command-line arguments
void parse_args(int argc, char *argv[], int *num_flow, int *flow_size, char *congestion_ctl)
{
    // First argument is the number of flows
    if (argc < 2)
    {
        // Default number of flows is 100
        *num_flow = 100;
    }
    else
    {
        *num_flow = atoi(argv[1]);

        // Validate the number of flows is a positive integer
        if (*num_flow <= 0)
        {
            perror("Please enter a valid value for the number of flows.\n");
            exit(EXIT_FAILURE);
        }
    }

    // Second argument is the file name to read the flow size from
    if (argc < 2)
    {
        // Default flow size is 80 KB
        *flow_size = 80 * 1024;
    }
    else
    {
        FILE *fp = fopen(argv[2], "r");
        if (fp == NULL)
        {
            perror("Error opening file");
            exit(EXIT_FAILURE);
        }
        fseek(fp, 0L, SEEK_END);
        *flow_size = ftell(fp); // Use the file size as the flow size
        fclose(fp);
    }

    // Third argument is the congestion control algorithm
    if (argc < 3)
    {
        // Default congestion control algorithm is cubic
        strcpy(congestion_ctl, "cubic");
    }
    else
    {
        // Use provided congestion control algorithm
        strcpy(congestion_ctl, argv[3]);
    }
}

// Main client function
int main(int argc, char *argv[])
{
    int sockfd;
    struct sockaddr_in servaddr;
    int num_flow, flow_size;
    char congestion_ctl[256];

    // Parse command-line arguments
    parse_args(argc, argv, &num_flow, &flow_size, congestion_ctl);
    printf("Number of flows: %d, Flow size: %d, Congestion control: %s\n", num_flow, flow_size, congestion_ctl);

    for (int j = 0; j < num_flow; j++)
    {
        // Create a new socket
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd < 0)
        {
            perror("Socket creation failed");
            exit(EXIT_FAILURE);
        }
        printf("Socket successfully created..\n");

        // Set up server address
        bzero(&servaddr, sizeof(servaddr));
        servaddr.sin_family = AF_INET;
        servaddr.sin_addr.s_addr = inet_addr(DEST_IP);
        servaddr.sin_port = htons(PORT);

        // Set TCP_NODELAY option to disable Nagle's algorithm
        int on = 1;
        if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, (void *)&on, sizeof(on)) == -1)
        {
            perror("TCP_NODELAY failure");
        }

        // Clear TCP_CORK option for each connection
        int off = 0;
        if (setsockopt(sockfd, IPPROTO_TCP, TCP_CORK, (void *)&off, sizeof(off)) == -1)
        {
            perror("TCP_CORK failure");
        }

        // Set the receive buffer size to the defined value
        int size = BUFFSIZE;
        if (setsockopt(sockfd, SOL_SOCKET, SO_RCVBUFFORCE, (char *)&size, sizeof(size)) == -1)
        {
            perror("SO_RCVBUF failure");
        }

        // Set the congestion control algorithm
        if (setsockopt(sockfd, IPPROTO_TCP, TCP_CONGESTION, (char *)congestion_ctl, sizeof(congestion_ctl)) != 0)
        {
            perror("Congestion control algorithm specification error");
        }

        // Set SO_LINGER option to control the behavior on shutdown
        struct linger so_linger;
        so_linger.l_onoff = 1;   // Enable SO_LINGER
        so_linger.l_linger = 30; // Wait for 30 seconds for the connection to close
        if (setsockopt(sockfd, SOL_SOCKET, SO_LINGER, &so_linger, sizeof so_linger) != 0)
        {
            perror("SO_LINGER failure");
        }

        // Connect to the server
        if (connect(sockfd, (SA *)&servaddr, sizeof(servaddr)) < 0)
        {
            perror("Connection failed");
            close(sockfd);
            continue;
        }

        // Process received data
        receive_data(connfd, flow_size);

        // Shutdown and close the socket
        shutdown(sockfd, SHUT_WR);
        close(sockfd);
    }

    return 0;
}
