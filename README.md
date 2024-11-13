

```
curl -v -X PUT  -d "{\"upper_layer_text\": \"Hello world\"}" http://192.168.1.101:8088/properties/upper_layer_text
```


**Docker**
```
sudo docker run -p 8316:8642  --privileged -e "out:warn:12"  grro/pi_gpio_webthing:0.0.2
```
