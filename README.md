

```
curl -v -X PUT  -d "{\"upper_layer_text\": \"Hello world\"}" http://192.168.1.101:8088/properties/upper_layer_text
```


**Docker**
```
sudo docker rm -f warn_led
sudo docker run --name warn_led -p 8316:8642  --privileged -e "led:warn:12"  grro/pi_gpio_webthing:0.0.5
```
