

```
curl -v -X PUT  -d "{\"upper_layer_text\": \"Hello world\"}" http://192.168.1.101:8088/properties/upper_layer_text
```


**Docker**
```
sudo docker run -p 8070:8070 --device /dev/i2c-1:/dev/i2c-1 -e name="WebServer" -e i2c_expander=PCF8574 -e i2c_address=0x27  grro/pi_display_webthing:0.2.5
```