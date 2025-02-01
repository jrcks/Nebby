#include <netdb.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>

#define PORT 8081
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
void send_data(int connfd, char *web_file)
{
    // Use the file size as the flow size
    FILE *fp = fopen(web_file, "r");
    if (fp == NULL)
    {
        perror("Error opening file for reading");
        exit(EXIT_FAILURE);
    }

    // Get the file size
    fseek(fp, 0L, SEEK_END);
    long file_size = ftell(fp);
    rewind(fp);
    printf("The size to send is %ld B\n", file_size);

    // Buffer to store file data
    char buff[file_size];

    // Send the file data
    size_t bytes_sent = 0;
    while (bytes_sent < file_size)
    {
        // Read data from the file
        size_t num_bytes = fread(buff, 1, file_size, fp);
        if (num_bytes == 0) {
            if (feof(fp)) {
                break; // End of file
            } else {
                perror("Error reading file");
                fclose(fp);
                exit(EXIT_FAILURE);
            }
        }

        // Send data to the client
        size_t bytes_sent_now = 0;
        while (bytes_sent_now < num_bytes) 
        {
            // Send whats remaining
            size_t now_sent = send(connfd, buff + bytes_sent_now, num_bytes - bytes_sent_now, 0);
            if (now_sent == -1) 
            {
                perror("Send failed");
                fclose(fp);
                exit(EXIT_FAILURE);
            }

            // Update the local total sent byte count
            bytes_sent_now += now_sent;
        }

        // Update the total
        bytes_sent += bytes_sent_now;
    }

    // Close the file
    fclose(fp);

    // Log the total number of bytes sent
    printf("The size sent is %ld B\n", bytes_sent);
}

// Function to check and parse command-line arguments
void parse_args(int argc, char *argv[], char *web_file, char *congestion_ctl)
{
    // First argument is the file to serve
    if (argc < 2)
    {
        // Default file is index.html
        realpath("./index.html", web_file);
    }
    else
    {
        // Use the provided file
        realpath(argv[1], web_file);
    }

    // Validate the file to server can be accessed
    if (access(web_file, F_OK) < 0)
    {
        perror("File to serve does not exist");
    }

    // Second argument is the congestion control algorithm
    if (argc < 3)
    {
        // Default congestion control algorithm is cubic
        strcpy(congestion_ctl, "cubic");
    }
    else
    {
        // Use provided congestion control algorithm
        strcpy(congestion_ctl, argv[2]);
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
        if (getsockopt(sockfd, SOL_TCP, TCP_INFO, &(recording_elems[i].tcp_info), &tcp_info_length) < 0)
        {
            perror("Failed to get TCP info");
            break;
        }
    }
}

void save_statistics(int id, struct Recording_elem *recording_elems)
{
    // Write recorded statistics to the file
    FILE *statistics = fopen(LOG_FILE, "a+");
    if (statistics == NULL)
    {
        perror("Failed to open statistics file");
        return;
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
                id,
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
    printf("Saved statistics...\n");
}

// Main server function
int main(int argc, char *argv[])
{
    // Parse command-line arguments
    char web_file[256], congestion_ctl[256];
    parse_args(argc, argv, web_file, congestion_ctl);
    printf("File to serve is %s, congestion control algorithm is %s\n", web_file, congestion_ctl);

    // Check/prepare the statistics file
    check_file_exist(LOG_FILE);

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

    // Set SO_LINGER option to control the behavior on shutdown
    struct linger so_linger;
    so_linger.l_onoff = 1;   // Enable SO_LINGER
    so_linger.l_linger = 30; // Wait for 30 seconds for the connection to close
    if (setsockopt(sockfd, SOL_SOCKET, SO_LINGER, &so_linger, sizeof(so_linger)) < 0)
    {
        perror("SO_LINGER failure on the receiver!");
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

    // Serve until user presses ctrl + c
    int id = 0;
    while (1)
    {
        // Accept incoming client connection
        int connfd = accept(sockfd, (SA *)&clientaddr, &len);
        if (connfd < 0)
        {
            perror("Server accept failed");
            exit(EXIT_FAILURE);
        }
        printf("[#%d] Server accepted the client...\n", ++id);

        // Set TCP_NODELAY option to disable Nagle's algorithm
        if (setsockopt(connfd, IPPROTO_TCP, TCP_NODELAY, &(int){1}, sizeof(int)) < 0)
        {
            perror("TCP_NODELAY failure");
        }

        // Clear TCP_CORK option for each connection
        if (setsockopt(connfd, IPPROTO_TCP, TCP_CORK, &(int){0}, sizeof(int)) < 0)
        {
            perror("TCP_CORK failure");
        }

        // TODO: Example value
        // Set the busy poll option
        if (setsockopt(connfd, SOL_SOCKET, SO_BUSY_POLL, &(int){50}, sizeof(int)) < 0)
        {
            perror("SO_BUSY_POLL failure");
        }

        // Set the send buffer size to the defined value
        if (setsockopt(connfd, SOL_SOCKET, SO_SNDBUFFORCE, &(int){BUFFSIZE}, sizeof(int)) < 0)
        {
            perror("SO_SNDBUFFORCE failure");
        }

        // Enable TCP_QUICKACK option every connection to reduce acknowledgment latency
        if (setsockopt(connfd, IPPROTO_TCP, TCP_QUICKACK, &(int){1}, sizeof(int)) < 0)
        {
            perror("TCP_QUICKACK failure");
        }

        // Set the congestion control algorithm
        if (setsockopt(connfd, IPPROTO_TCP, TCP_CONGESTION, congestion_ctl, sizeof(congestion_ctl)) < 0)
        {
            perror("Congestion control algorithm failure");
        }

        // Prepare thread structure for recording
        struct Thread_Record_Struct thread_record_struct = {sockfd = sockfd};
        pthread_t tid;

        // Create the thread for recording TCP statistics
        if (pthread_create(&tid, NULL, thread_recording, &thread_record_struct) != 0)
        {
            perror("Failed to create thread");
        }
        printf("Created a thread for recording.\n");

        // Send data
        send_data(connfd, web_file);

        // Close the connection
        close(connfd);
        printf("Server closed connection to client...\n");

        // Save statistics after recording thread finishes
        pthread_join(tid, NULL);
        save_statistics(id, thread_record_struct.recording_elems);
    }

    return 0;
}
