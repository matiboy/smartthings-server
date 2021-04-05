# SmartThings Proxy

```
$ python server.py --token <Smartthings token> --api-key <Your choice of api key> --port <port>
```

# tunnel

ssh -tR 10000:localhost:9999 static-ip-forwarder /home/ec2-user/tunnel/sirtunnel.py --debug --check-availability --replace matodie.local.tunnel.redapesolutions.com  10000