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
#define DEST_IP "127.0.0.1"
#define BUFFSIZE (150 * 1024) // 150 KB Buffer size
#define RECORD_PERIOD 50000
#define FILENAME "stats.csv"
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
void send_data(int sockfd, int flow_size)
{
    // Buffer for data to send
    char buff[flow_size];
    memset(buff, 0, flow_size);

    // Enable TCP_QUICKACK for each send
    int on = 1;
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_QUICKACK, &on, sizeof(on)) == -1)
    {
        perror("TCP_QUICKACK Failure");
        exit(EXIT_FAILURE);
    }

    // Send data
    int size = send(sockfd, buff, flow_size, 0);
    printf("The size sent is %d B\n", size);
}

// Function to check and parse command-line arguments
void parse_args(int argc, char *argv[], int *num_flow, int *flow_size, char *congestion_ctl)
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

    // Second argument is the flow size
    if (argc < 3)
    {
        // Default flow size is 80 KB
        *flow_size = 80 * 1024;
    }
    else
    {
        // Use the provided flow size in KB
        *flow_size = (int)(atof(argv[2]) * 1024);

        // Check if the flow size is valid
        if (*flow_size <= 0)
        {
            fprintf(stderr, "Error: please enter a valid value for the flow size\n");
            exit(EXIT_FAILURE);
        }
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

// Main client function
int main(int argc, char *argv[])
{
    int sockfd;
    struct sockaddr_in servaddr;
    int num_flow, flow_size;
    char congestion_ctl[256];

    // Check/prepare the statistics file
    check_file_exist(FILENAME);

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

        // Set the busy poll option
        int value = 50; // Todo: Example value
        if (setsockopt(sockfd, SOL_SOCKET, SO_BUSY_POLL, (char *)&value, sizeof(value)) == -1)
        {
            perror("SO_BUSY_POLL failure");
        }

        // Set the send buffer size to the defined value
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
        send_data(sockfd, flow_size);

        // Shutdown the socket
        shutdown(sockfd, SHUT_WR);
        pthread_join(tid, NULL); // Wait for the recording thread to finish

        // Write recorded statistics to the file
        FILE *statistics = fopen(FILENAME, "a+");
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

        // Clean up and close the socket
        fclose(statistics);
        close(sockfd); // Close the socket after usage
        usleep(500);   // Sleep for a short duration
    }

    return 0;
}
