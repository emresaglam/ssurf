# SSRF DNS Resolution Automation.

## Why?
This is somehow a corner case automation. More why here. 

## What?
This script spins up two servers:
- A web server (REST API) that receives an IP on endpoint /ip/10.0.0.1 as input
- A DNS server that resolves ANY domain query to the IP that was received by the we server REST API. (With TTL 0 so that you can change the IP each time ;) 

It creates a process per server and communicates between each other by a process queue (to carry over IPs)

### But really... WHY?
I wanted to a little research on automating this attack after a real life scenario. Maybe you'll encounter a similar thing and this might be useful :)

## How?
* Do a `pip install -r requirements.txt` This will install Klein and Twisted...
* Run the server: `python ssurf.py`
* Send an IP to the REST API: `curl http://localhost:8080/ip/10.0.0.1`
* Do a resolution of any domain name to your local DNS server on port 10053: `dig -p 10053 emresaglam.com @localhost`
* You should see the domain resolving to the IP that you just sent to your server:
```$ dig -p 10053 emresaglam.com @localhost

; <<>> DiG 9.10.6 <<>> -p 10053 emresaglam.com @localhost
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 61302
;; flags: qr ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;emresaglam.com.			IN	A

;; ANSWER SECTION:
emresaglam.com.		0	IN	A	10.0.0.1

;; Query time: 4 msec
;; SERVER: 127.0.0.1#10053(127.0.0.1)
;; WHEN: Sun May 20 21:05:28 PDT 2018
;; MSG SIZE  rcvd: 48
```

* Rinse and repeat.