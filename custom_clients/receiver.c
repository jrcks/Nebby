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

#define PORT 8081
#define BUFFSIZE (150 * 1024)
#define OUT_FILE "/dev/null"
#define SA struct sockaddr

// Function to receive data from the server and store it in a file
void *receive_data(int *connfd_ptr)
{
    int connfd = *((int *)connfd_ptr);
    free(connfd_ptr); // Free the memory allocated for connfd_ptr

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
    printf("Total Bytes Received: %d B\n", bytes_recv);

    // Proper exit from thread function
    pthread_exit(NULL);
}

// Main client function
int main(int argc, char *argv[])
{
    // Create a new socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    printf("Socket successfully created..\n");

    // Set SO_REUSEADDR to reuse the same port
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) < 0)
    {
        perror("SO_REUSEADDR failure");
    }

    // Assign IP and PORT to the socket
    struct sockaddr_in servaddr;
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;                // IPv4
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY); // Accept connections on any available network interface
    servaddr.sin_port = htons(PORT);              // Convert port number to network byte order

    // Bind the socket to the assigned IP and PORT
    if (bind(sockfd, (SA *)&servaddr, sizeof(servaddr)) != 0)
    {
        perror("Socket bind failed");
        exit(EXIT_FAILURE);
    }
    printf("Socket successfully binded..\n");

    // Prepare the server to listen for incoming connections
    if (listen(sockfd, 5) != 0)
    {
        perror("Listen failed");
        exit(EXIT_FAILURE);
    }
    printf("Server listening..\n");

    // Initialize the length of the client address structure
    struct sockaddr_in clientaddr;
    socklen_t len = sizeof(clientaddr);

    while (1)
    {
        // Accept incoming client connection
        int connfd = accept(sockfd, (SA *)&clientaddr, &len);
        if (connfd < 0)
        {
            perror("Server accept failed");
            exit(EXIT_FAILURE);
        }
        printf("Server accepted the client...\n");

        // Set SO_LINGER option to control the behavior on shutdown
        struct linger so_linger;
        so_linger.l_onoff = 1;   // Enable SO_LINGER
        so_linger.l_linger = 30; // Wait for 30 seconds for the connection to close
        if (setsockopt(connfd, SOL_SOCKET, SO_LINGER, &so_linger, sizeof(so_linger)) < 0)
        {
            perror("SO_LINGER failure");
        }

        // Set TCP_NODELAY option to disable Nagle's algorithm
        if (setsockopt(connfd, IPPROTO_TCP, TCP_NODELAY, &(int){1}, sizeof(int)) < 0)
        {
            perror("TCP_NODELAY failure");
        }

        // Set the receive buffer size to the defined value
        if (setsockopt(connfd, SOL_SOCKET, SO_RCVBUFFORCE, &(int){BUFFSIZE}, sizeof(int)) < 0)
        {
            perror("SO_RCVBUFFORCE failure");
        }

        // Create a new thread for the connection handling
        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, receive_data, connfd) < 0)
        {
            perror("Could not create thread");
            close(connfd);
            continue;
        }

        // Detach the thread to avoid memory leaks
        pthread_detach(thread_id);
    }

    // Close the listening socket when done
    close(sockfd);
    return 0;
}
