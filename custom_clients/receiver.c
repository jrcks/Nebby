#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
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
    pid_t pid = getpid();

    // Open the file for writing
    FILE *fp = fopen(OUT_FILE, "w+");
    if (fp == NULL)
    {
        perror("Error opening file for writing");
        return;
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
            return;
        }
        else if (num_bytes == 0)
        {
            break; // Connection has been closed by the server
        }
        printf("[%d] Received %d Bytes\n", pid, num_bytes);

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

    // Close the file and socket
    fclose(fp);
    close(connfd);

    // Log the total number of bytes received
    printf("[%d] Received %d Bytes in total\n", pid, bytes_recv);
}

// Main receiver function
int main(int argc, char *argv[])
{
    // Create a new socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    printf("Socket successfully created\n");

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
    printf("Socket successfully bound\n");

    // Prepare the server to listen for incoming connections
    if (listen(sockfd, 5) != 0)
    {
        perror("Listen failed");
        exit(EXIT_FAILURE);
    }
    printf("Server listening on port %d\n", PORT);

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

        // Create a new process to handle the client connection
        pid_t pid = fork();
        if (pid < 0)
        {
            perror("Fork failed");
            close(connfd);
            continue;
        }

        // In the child process
        if (pid == 0)
        {
            // Get the process ID
            pid = getpid();

            // Child doesn't need the listening socket
            close(sockfd);

            // Get client's IP address
            char *client_ip = inet_ntoa(clientaddr.sin_addr);
            printf("[%d] Server accepted the client with IP %s\n", pid, client_ip ? client_ip : "unknown");

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

            // Receive data from the sender
            receive_data(connfd);

            // Exit after receiving data
            exit(EXIT_SUCCESS);
        }

        // Close the connection in the parent process
        close(connfd);
    }

    // Close the listening socket when done
    close(sockfd);
    return 0;
}
