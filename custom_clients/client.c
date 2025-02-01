#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <pthread.h>
#include <errno.h>

#define PORT 8081
#define BUFFSIZE (150 * 1024)
#define OUT_FILE "/dev/null"
#define SA struct sockaddr

// Function to receive data from the server and store it in a file
void receive_data(int connfd)
{
    // Buffer to store received data temporarily
    char buff[BUFFSIZE];
    bzero(buff, sizeof(buff));

    // Open the file for writing
    FILE *fp = fopen(OUT_FILE, "w+");
    if (fp == NULL)
    {
        perror("Error opening file for writing");
        exit(EXIT_FAILURE);
    }

    // Receive data from the server
    int bytes_recv = 0;
    while (1)
    {
        // Receive data from the server
        int num_bytes = recv(connfd, buff, sizeof(buff), 0);
        if (num_bytes < 0)
        {
            perror("Receive failed");
            fclose(fp);
            exit(EXIT_FAILURE);
        }
        else if (num_bytes == 0)
        {
            break; // Connection has been closed by the server
        }

        // Write received bytes to the file
        size_t written = fwrite(buff, 1, num_bytes, fp);
        if (written < num_bytes)
        {
            perror("Failed to write all data to file");
            break;
        }

        // Ensure data is written to the file
        fflush(fp);

        bytes_recv += num_bytes; // Update the total received byte count
    }

    // Close the file
    fclose(fp);

    // Log the total number of bytes received
    printf("Total Bytes Received: %d\n", bytes_recv);
}

// Function to check and parse command-line arguments
void parse_args(int argc, char *argv[], char *dest_ip, int *num_conns)
{
    // First argument is the destination ip address
    if (argc < 2)
    {
        // Default destination ip address is localhost
        strcpy(dest_ip, "127.0.0.1");
    }
    else
    {
        // Use provided destination ip address
        strcpy(dest_ip, argv[1]);
    }

    // Second argument is the number of connections to make
    if (argc < 3)
    {
        // Default number of connections is 1
        *num_conns = 1;
    }
    else
    {
        *num_conns = atoi(argv[2]);

        // Validate the number of connections is a positive integer
        if (*num_conns <= 0)
        {
            perror("Please enter a valid value for the number of connections");
            exit(EXIT_FAILURE);
        }
    }
}

// Main client function
int main(int argc, char *argv[])
{
    char dest_ip[256];
    int num_conns;

    // Parse command-line arguments
    parse_args(argc, argv, dest_ip, &num_conns);
    printf("Connecting %d times to %s\n", num_conns, dest_ip);

    // Set up server address
    struct sockaddr_in servaddr;
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr(dest_ip);
    servaddr.sin_port = htons(PORT);

    for (int conn = 0; conn < num_conns; conn++)
    {
        // Create a new socket
        int sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd < 0)
        {
            perror("Socket creation failed");
            exit(EXIT_FAILURE);
        }
        printf("Socket successfully created..\n");

        // Set SO_LINGER option to control the behavior on shutdown
        struct linger so_linger;
        so_linger.l_onoff = 1;   // Enable SO_LINGER
        so_linger.l_linger = 30; // Wait for 30 seconds for the connection to close
        if (setsockopt(sockfd, SOL_SOCKET, SO_LINGER, &so_linger, sizeof(so_linger)) < 0)
        {
            perror("SO_LINGER failure");
        }

        // Set TCP_NODELAY option to disable Nagle's algorithm
        if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &(int){1}, sizeof(int)) < 0)
        {
            perror("TCP_NODELAY failure");
        }

        // Set the receive buffer size to the defined value
        if (setsockopt(sockfd, SOL_SOCKET, SO_RCVBUFFORCE, &(int){BUFFSIZE}, sizeof(int)) < 0)
        {
            perror("SO_RCVBUFFORCE failure");
        }

        // Connect to the server
        if (connect(sockfd, (SA *)&servaddr, sizeof(servaddr)) < 0)
        {
            perror("Connection failed");
            close(sockfd);
            continue;
        }

        // Process received data
        receive_data(sockfd);

        // Shutdown and close the socket
        shutdown(sockfd, SHUT_WR);
        close(sockfd);
    }

    return 0;
}
