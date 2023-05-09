### USING aioquic library

Install the library from : https://github.com/aiortc/aioquic

    cd aioquic
    pip install -e .
    pip install asgiref dnslib "flask<2.2" httpbin starlette "werkzeug<2.1" wsproto

Move to Nebby/quic_clients 
    cd Nebby/quic_clients

The command to run an http3 client

    python3 cloudflare_aioquic.py --output-dir ./output https://cloudflare-quic.com

Attention - https://www.cloudflare-quic.com doesn't work, https://cloudflare-quic.com works.  

  
In the output folder you will see index.html. Open it in the web browser, it should show that you used http3. 

To check if the website you are posing an https request to supports http3 and therefore quic, you can use  https://http3check.net. It checks if the response header of the website checked contains 'h3' in its 'alt-svc' parameter.   
However there are websites which do not do this but still might support HTTP3, eg. www.reddit.com  
Another tool I found : https://pororoca.io - similar to postman, but supports HTTP3 (Not tinkered with yet.)  

Other websites you can try: 
1. www.youtube.com
2. www.open.spotify.com 
3. www.music.youtube.com
  
The size of the file downloaded depends on the part of the website which supports QUIC. If you try www.spotify.com, it will download less data than if you try open.spotify.com. 
  
If you try a website that doesn't support QUIC, the script gives an error. (Will handle this error soon.)


### Using headless chrome
### Using headless firefox

(Update soon, have figured out a way to work though).