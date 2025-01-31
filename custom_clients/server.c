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
#include <pthread.h>

#define PORT 8080
#define BUFFSIZE (150 * 1024)
#define RECORD_PERIOD 50000
#define LOG_FILE "stats.csv"
#define SA struct sockaddr

// Structure to hold TCP statistics
struct Recording_elem
{
    int64_t ts;               // Timestamp
    struct timespec timespec; // Time specification
    struct tcp_info tcp_info; // TCP information
};

// Structure to pass arguments to the recording thread
struct Thread_Record_Struct
{
    int sockfd;
    struct Recording_elem recording_elems[RECORD_PERIOD];
};

// Function to check if the statistics file exists and create it if it doesn't
void check_file_exist(const char *filename)
{
    // Check if file exists
    if (access(filename, F_OK))
    {
        printf("Creating the stats file: %s\n", filename);
        FILE *file = fopen(filename, "w+");
        if (file == NULL)
        {
            perror("Error creating file");
            return;
        }

        // Write the header to the stats file
        fprintf(file, "flow_id\tts(seconds.nanoseconds)\ttcpi_state\ttcpi_ca_state\t"
                      "tcpi_retransmits\ttcpi_probes\ttcpi_backoff\ttcpi_options\t"
                      "tcpi_snd_wscale\ttcpi_rcv_wscale\ttcpi_rto\ttcpi_ato\t"
                      "tcpi_snd_mss\ttcpi_rcv_mss\ttcpi_unacked\ttcpi_sacked\t"
                      "tcpi_lost\ttcpi_retrans\ttcpi_fackets\t"
                      "tcpi_last_data_sent\ttcpi_last_ack_sent\t"
                      "tcpi_last_data_recv\ttcpi_last_ack_recv\t"
                      "tcpi_pmtu\ttcpi_rcv_ssthresh\ttcpi_rtt\ttcpi_rttvar\t"
                      "tcpi_snd_ssthresh\ttcpi_snd_cwnd\ttcpi_advmss\t"
                      "tcpi_reordering\ttcpi_rcv_rtt\ttcpi_rcv_space\t"
                      "tcpi_total_retrans\n");

        fclose(file);
    }
    else
    {
        printf("The stats file %s exists\n", filename);
    }
}

// Function to handle data sending over the socket
void send_data(int sockfd, char *web_file)
{
    // Enable TCP_QUICKACK option every connection to reduce acknowledgment latency
    int on = 1;
    if (setsockopt(connfd, IPPROTO_TCP, TCP_QUICKACK, (void *)&on, sizeof(on)) == -1)
    {
        perror("TCP_QUICKACK Failure");
        exit(EXIT_FAILURE);
    }

    // Use the file size as the flow size
    FILE *fp = fopen(web_file, "r");
    if (fp == NULL)
    {
        perror("Error opening file for reading");
        exit(EXIT_FAILURE);
    }

    // Get the file size
    fseek(fp, 0L, SEEK_END);
    int flow_size = ftell(fp);

    // Buffer to store file data
    char buff[flow_size];
    bzero(buff, flow_size);

    // Send the file data
    int bytes_sent = 0;
    while (1)
    {
        // Read data from the file
        int num_bytes = fread(buff, 1, flow_size, fp);
        if (num_bytes == 0)
        {
            break; // End of file
        }

        // Send data to the client
        int num_sent = send(sockfd, buff, num_bytes, 0);
        if (num_sent == -1)
        {
            perror("Send Failed");
            exit(EXIT_FAILURE);
        }
        bytes_sent += num_sent; // Update the total sent byte count
    }

    // Close the file
    fclose(fp);

    // Log the total number of bytes sent
    printf("The size sent is %d B\n", bytes_sent);
}

// Function to check and parse command-line arguments
void parse_args(int argc, char *argv[], int *num_flow, char *web_file, char *congestion_ctl)
{
    // First argument is the number of flows
    if (argc < 2)
    {
        // Default number of flows is 5
        *num_flow = 5;
    }
    else
    {
        *num_flow = atoi(argv[1]);

        // Check if the number of flows is valid
        if (*num_flow <= 0)
        {
            fprintf(stderr, "Error: please enter a valid value for the number of flows\n");
            exit(EXIT_FAILURE);
        }
    }

    // Second argument is the file to serve
    if (argc < 3)
    {
        // Default file is index.html
        strcpy(web_file, "index.html");
    }
    else
    {
        // Use the provided file
        strcpy(web_file, argv[2]);
    }

    // Third argument is the congestion control algorithm
    if (argc < 4)
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

// Thread function to record TCP statistics
void *thread_recording(void *arg)
{
    // Initialize the recording structure
    struct Thread_Record_Struct *rec_struct = (struct Thread_Record_Struct *)arg;
    int sockfd = rec_struct->sockfd;
    struct Recording_elem *recording_elems = rec_struct->recording_elems;
    int tcp_info_length = sizeof(recording_elems[0].tcp_info);

    for (int i = 0; i < RECORD_PERIOD; i++)
    {
        // Get current time
        clock_gettime(CLOCK_REALTIME, &(recording_elems[i].timespec));

        // Get TCP information from the socket
        if (getsockopt(sockfd, SOL_TCP, TCP_INFO, &(recording_elems[i].tcp_info), &tcp_info_length) != 0)
        {
            perror("Failed to get TCP info");
            break;
        }
    }
}

// Main server function

int main(int argc, char *argv[])
{
    int sockfd, connfd;
    socklen_t len;
    struct sockaddr_in servaddr, cli;
    int num_flow;
    char web_file[256];
    char congestion_ctl[256];

    // Parse command-line arguments
    parse_args(argc, argv, &num_flow, web_file, congestion_ctl);
    printf("File to serve is %d, congestion control algorithm is %s\n", web_file, congestion_ctl);

    // Check/prepare the statistics file
    check_file_exist(LOG_FILE);

    // Create a new socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    printf("Socket successfully created..\n");

    // Assign IP and PORT to the socket
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
    len = sizeof(cli);
    for (int i = 0; i < num_flow; i++)
    {
        // Accept incoming client connection
        connfd = accept(sockfd, (SA *)&cli, &len);
        if (connfd < 0)
        {
            perror("Server accept failed");
            exit(EXIT_FAILURE);
        }
        printf("# %d Server accepted the client...\n", i + 1);

        // Set TCP_NODELAY option to disable Nagle's algorithm
        int on = 1;
        if (setsockopt(connfd, IPPROTO_TCP, TCP_NODELAY, (void *)&on, sizeof(on)) == -1)
        {
            perror("TCP_NODELAY failure");
        }

        // Clear TCP_CORK option for each connection
        int off = 0;
        if (setsockopt(connfd, IPPROTO_TCP, TCP_CORK, (void *)&off, sizeof(off)) == -1)
        {
            perror("TCP_CORK failure");
        }

        // Set the busy poll option
        int value = 50; // TODO: Example value
        if (setsockopt(sockfd, SOL_SOCKET, SO_BUSY_POLL, (char *)&value, sizeof(value)) == -1)
        {
            perror("SO_BUSY_POLL failure");
        }

        // Set the send buffer size to the defined value
        // TODO: SO_RCVBUFFORCE is not the send buffer
        int size = BUFFSIZE;
        if (setsockopt(connfd, SOL_SOCKET, SO_RCVBUFFORCE, &size, sizeof(size)) == -1)
        {
            perror("SO_RCVBUF failure");
        }

        // Set the congestion control algorithm
        if (setsockopt(connfd, IPPROTO_TCP, TCP_CONGESTION, congestion_ctl, sizeof(congestion_ctl)) != 0)
        {
            perror("Congestion control algorithm specification error");
        }

        // Set SO_LINGER option to control the behavior on shutdown
        struct linger so_linger;
        so_linger.l_onoff = 1;   // Enable SO_LINGER
        so_linger.l_linger = 30; // Wait for 30 seconds for the connection to close
        if (setsockopt(connfd, SOL_SOCKET, SO_LINGER, &so_linger, sizeof so_linger) != 0)
        {
            perror("SO_LINGER failure on the receiver!");
        }

        // Prepare thread structure for recording
        struct Thread_Record_Struct thread_record_struct = {sockfd = sockfd};
        struct Recording_elem *recording_elems = thread_record_struct.recording_elems;
        pthread_t tid;

        // Create the thread for recording TCP statistics
        if (pthread_create(&tid, NULL, thread_recording, &thread_record_struct) != 0)
        {
            perror("Failed to create thread");
            close(sockfd);
            continue;
        }
        printf("Created a thread for recording.\n");

        // Send data
        send_data(sockfd, web_file);

        // Close the connection
        close(connfd);

        // Wait for the recording thread to finish
        pthread_join(tid, NULL);

        // Write recorded statistics to the file
        FILE *statistics = fopen(LOG_FILE, "a+");
        if (statistics == NULL)
        {
            perror("Failed to open statistics file");
            close(sockfd);
            continue;
        }

        // Save recorded statistics
        for (int i = 0; i < RECORD_PERIOD; i++)
        {
            recording_elems[i].ts = (int64_t)recording_elems[i].timespec.tv_sec * 1e9 + (int64_t)recording_elems[i].timespec.tv_nsec;

            fprintf(statistics, "%d\t%lu.%lu\t"
                                "%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t"
                                "%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t"
                                "%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t"
                                "%u\t%u\t%u\t%u\n",
                    j + 1,
                    recording_elems[i].timespec.tv_sec,
                    recording_elems[i].timespec.tv_nsec,
                    recording_elems[i].tcp_info.tcpi_state,
                    recording_elems[i].tcp_info.tcpi_ca_state,
                    recording_elems[i].tcp_info.tcpi_retransmits,
                    recording_elems[i].tcp_info.tcpi_probes,
                    recording_elems[i].tcp_info.tcpi_backoff,
                    recording_elems[i].tcp_info.tcpi_options,
                    recording_elems[i].tcp_info.tcpi_snd_wscale,
                    recording_elems[i].tcp_info.tcpi_rcv_wscale,
                    recording_elems[i].tcp_info.tcpi_rto,
                    recording_elems[i].tcp_info.tcpi_ato,
                    recording_elems[i].tcp_info.tcpi_snd_mss,
                    recording_elems[i].tcp_info.tcpi_rcv_mss,
                    recording_elems[i].tcp_info.tcpi_unacked,
                    recording_elems[i].tcp_info.tcpi_sacked,
                    recording_elems[i].tcp_info.tcpi_lost,
                    recording_elems[i].tcp_info.tcpi_retrans,
                    recording_elems[i].tcp_info.tcpi_fackets,
                    recording_elems[i].tcp_info.tcpi_last_data_sent,
                    recording_elems[i].tcp_info.tcpi_last_ack_sent,
                    recording_elems[i].tcp_info.tcpi_last_data_recv,
                    recording_elems[i].tcp_info.tcpi_last_ack_recv,
                    recording_elems[i].tcp_info.tcpi_pmtu,
                    recording_elems[i].tcp_info.tcpi_rcv_ssthresh,
                    recording_elems[i].tcp_info.tcpi_rtt,
                    recording_elems[i].tcp_info.tcpi_rttvar,
                    recording_elems[i].tcp_info.tcpi_snd_ssthresh,
                    recording_elems[i].tcp_info.tcpi_snd_cwnd,
                    recording_elems[i].tcp_info.tcpi_advmss,
                    recording_elems[i].tcp_info.tcpi_reordering,
                    recording_elems[i].tcp_info.tcpi_rcv_rtt,
                    recording_elems[i].tcp_info.tcpi_rcv_space,
                    recording_elems[i].tcp_info.tcpi_total_retrans);
        }

        // Close the statistics file
        fclose(statistics);
    }

    // Close the socket after all connections are handled
    shutdown(sockfd, SHUT_WR);

    return 0;
}
