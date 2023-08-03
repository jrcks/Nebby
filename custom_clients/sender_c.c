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
#define BUFFSIZE 150 * 1024
#define RECORD_PERIOD 50000
#define FILENAME "stats.csv"
#define SA struct sockaddr
#define DEST_IP "127.0.0.1"

struct Recording_elem {
    int64_t ts;
    struct timespec timespec;
    struct tcp_info tcp_info;
} ;  


struct Thread_Record_Struct {
    int sockfd;
    struct Recording_elem recording_elems[RECORD_PERIOD];
} ;  


void check_file_exist(char *filename){

    if( access(filename, F_OK )){
        printf("The stats file %s doesn't exist\n",filename);
        FILE *tmp;

        tmp = fopen(filename, "w+" );

        fprintf(tmp,
            "flow_id\t\
            ts(seconds.nanoseconds)\t\
            tcpi_state\t\
            tcpi_ca_state\t\
            tcpi_retransmits\t\
            tcpi_probes\t\
            tcpi_backoff\t\
            tcpi_options\t\
            tcpi_snd_wscale\t\
            tcpi_rcv_wscale\t\
            tcpi_rto\t\
            tcpi_ato\t\
            tcpi_snd_mss\t\
            tcpi_rcv_mss\t\
            tcpi_unacked\t\
            tcpi_sacked\t\
            tcpi_lost\t\
            tcpi_retrans\t\
            tcpi_fackets\t\
            tcpi_last_data_sent\t\
            tcpi_last_ack_sent\t\
            tcpi_last_data_recv\t\
            tcpi_last_ack_recv\t\
            tcpi_pmtu\t\
            tcpi_rcv_ssthresh\t\
            tcpi_rtt\t\
            tcpi_rttvar\t\
            tcpi_snd_ssthresh\t\
            tcpi_snd_cwnd\t\
            tcpi_advmss\t\
            tcpi_reordering\t\
            tcpi_rcv_rtt\t\
            tcpi_rcv_space\t\
            tcpi_total_retrans\n"
        );

        if ( fflush(tmp) != 0 ) {
            fprintf(stderr, "Cannot flush buffers: %s\n", strerror(errno) );
        }

        fclose(tmp);

    }
    else{
        printf("The stats file %s exists\n",filename);
    }
}

void func(int sockfd, int flow_size)
{
    char buff[flow_size];

    bzero(buff,flow_size);

    //Set TCP_QUICKACK each send
    int on = 1;
    setsockopt( sockfd, IPPROTO_TCP, TCP_QUICKACK, (void *)&on, sizeof(on));
    
    int size = send(sockfd, buff, flow_size ,0);

    printf("The size sent is %d B\n",size);

}

void check_args(int argc, char *argv[], int* num_flow, int* flow_size,char* congestion_ctl){
    char* str_ptr;

    if(argc == 1)
        *num_flow = 5;
    else
        *num_flow = atoi(argv[1]);
    
    if( *num_flow == 0)
        printf("Error: please enter a valid value for the number of flows");
    
    // get the flow size
    if(argc < 2)
        *flow_size = 80 * 1024;
    else
        *flow_size = (int) (atof(argv[2]) * 1024);
    
    if( *flow_size == 0)
        printf("Error: please enter a valid value for the flow size");
    
    if(argc < 3)
        strcpy(congestion_ctl, "cubic");
    else
        strcpy(congestion_ctl, argv[3]);
}

void *thread_recording(void *vargp){

    struct Thread_Record_Struct *thread_record_struct =  (struct Thread_Record_Struct *)vargp;

    int sockfd = thread_record_struct->sockfd;

    struct Recording_elem *recording_elems = thread_record_struct->recording_elems;

    int tcp_info_length = sizeof(recording_elems[0].tcp_info);


    for(int i = 0; i < RECORD_PERIOD;i++ ){

        clock_gettime(CLOCK_REALTIME,&(recording_elems[i].timespec));

        if ( getsockopt( sockfd, SOL_TCP, TCP_INFO, (void *)&(recording_elems[i].tcp_info), &tcp_info_length ) != 0 ) {
            perror("Get tcp_info failure on the sender!");
            break;
        }

        //usleep(2);

    }

    return NULL;
}
   
int main(int argc, char *argv[])
{
    int sockfd, connfd;
    struct sockaddr_in servaddr, cli;

    int num_flow, flow_size;
    char congestion_ctl[256];
    struct linger so_linger;

    struct Thread_Record_Struct *thread_record_struct = (struct Thread_Record_Struct *)malloc(sizeof(struct Thread_Record_Struct));

    check_file_exist(FILENAME);

    FILE *statistics;

    statistics = fopen( FILENAME, "a+" );

    check_args(argc,argv,&num_flow,&flow_size,congestion_ctl);
    printf("Number of flow is %d, Flow size is %d, congestion control is %s\n",num_flow,flow_size,congestion_ctl);

    for(int j = 0; j < num_flow ; j++)
    {
        // socket create and varification
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd == -1) {
            printf("socket creation failed...\n");
            exit(0);
        }

        bzero(&servaddr, sizeof(servaddr));

        // assign IP, PORT
        servaddr.sin_family = AF_INET;
        servaddr.sin_addr.s_addr = inet_addr(DEST_IP);
        servaddr.sin_port = htons(PORT);

        //Set TCP_NODELAY each connection
        int on = 1;
        setsockopt( sockfd, IPPROTO_TCP, TCP_NODELAY, (void *)&on, sizeof(on));  

        //Clear TCP_NODELAY each connection
        int off = 0;
        setsockopt(sockfd, IPPROTO_TCP, TCP_CORK, (void *)&off, sizeof(off));
        
        //Set kernel poling option
        //TODO: Determine the value
        int value = 50;
        setsockopt(sockfd, SOL_SOCKET, SO_BUSY_POLL, (char *)&value, sizeof(value));

        //Set buffer size
        int size = BUFFSIZE;
        setsockopt(sockfd, SOL_SOCKET, SO_SNDBUFFORCE, (char *)&size, sizeof(size));

        // Set congestion control algorithm
        if(setsockopt(sockfd, IPPROTO_TCP, TCP_CONGESTION, (char *)congestion_ctl, sizeof(congestion_ctl))!=0){
            perror("congestion contorl algorithm specification error on the sender!");
            return -1;
        }

        // Set SO_LINGER
        so_linger.l_onoff = 1;
        so_linger.l_linger = 30;
        if(setsockopt(sockfd,SOL_SOCKET,SO_LINGER,&so_linger,sizeof so_linger)!= 0){
            perror("SO_LINGER failure on the sender!");
            return -1;
        }


        // connect the client socket to server socket
        if (connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
            printf("connection with the server failed...\n");
            exit(0);
        }

        thread_record_struct->sockfd = sockfd;
        pthread_t tid;
        pthread_create(&tid, NULL, thread_recording, thread_record_struct);
        printf("Created a thread\n");


        // function for chat
        func(sockfd,flow_size);

        //usleep(300);
        shutdown(sockfd, SHUT_WR);

        //pthread_cancel(tid);
        pthread_join(tid,NULL);

        struct Recording_elem *recording_elems = thread_record_struct->recording_elems;


        for(int i = 0;i < RECORD_PERIOD;i++){

            recording_elems[i].ts = (int64_t)(recording_elems[i].timespec.tv_sec) * (int64_t)1000000000 + (int64_t)(recording_elems[i].timespec.tv_nsec);

            fprintf(statistics,"%d\t%lu.%lu\t %u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\n",
                    j+1,
                    //recording_elems[i].ts,
                    recording_elems[i].timespec.tv_sec,
                    recording_elems[i].timespec.tv_nsec,
                    //
                    recording_elems[i].tcp_info.tcpi_state,
                    recording_elems[i].tcp_info.tcpi_ca_state,
                    recording_elems[i].tcp_info.tcpi_retransmits,
                    recording_elems[i].tcp_info.tcpi_probes,
                    recording_elems[i].tcp_info.tcpi_backoff,
                    recording_elems[i].tcp_info.tcpi_options,
                    recording_elems[i].tcp_info.tcpi_snd_wscale,
                    recording_elems[i].tcp_info.tcpi_rcv_wscale,
                    //
                    recording_elems[i].tcp_info.tcpi_rto,
                    recording_elems[i].tcp_info.tcpi_ato,
                    recording_elems[i].tcp_info.tcpi_snd_mss,
                    recording_elems[i].tcp_info.tcpi_rcv_mss,
                    //
                    recording_elems[i].tcp_info.tcpi_unacked,
                    recording_elems[i].tcp_info.tcpi_sacked,
                    recording_elems[i].tcp_info.tcpi_lost,
                    recording_elems[i].tcp_info.tcpi_retrans,
                    recording_elems[i].tcp_info.tcpi_fackets,
                    //Time
                    recording_elems[i].tcp_info.tcpi_last_data_sent,
                    recording_elems[i].tcp_info.tcpi_last_ack_sent,
                    recording_elems[i].tcp_info.tcpi_last_data_recv,
                    recording_elems[i].tcp_info.tcpi_last_ack_recv,
                    //Metric
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

                    recording_elems[i].tcp_info.tcpi_total_retrans
                    

                );
            if ( fflush(statistics) != 0 ) {
                fprintf(stderr, "Cannot flush buffers: %s\n", strerror(errno) );
            }
        }
        // sleep for several μs
        usleep(500);
    }

}