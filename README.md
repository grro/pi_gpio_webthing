

```
curl -v -X PUT  -d "{\"is-on\": true}" http://192.168.1.99:8316/0/properties/is-on
```


**Docker**
```
sudo docker rm -f warn_led
sudo docker run --name warn_led -p 8316:8642 --device /dev/gpiomem  -e "led:warn:12"  grro/pi_gpio_webthing:0.0.5
```
