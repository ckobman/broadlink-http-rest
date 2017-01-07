Broadlink HTTP server/proxy with REST API
==================================
Supported devices: RM/RM2/RM Pro/RM3/BlackBean/A1
-------------------------------------------------

Uses [python-broadlink](https://github.com/mjg59/python-broadlink)

Based and inspired by [BlackBeanControl](https://github.com/davorf/BlackBeanControl)


### Requirements

1. `python` (2.7)
2. `python-broadlink`
3. `netaddr`
4. `configparser`

### Installation

1. `git clone https://github.com/NightRang3r/broadlink-http-rest`
2. `sudo pip install broadlink`
3. `sudo pip install netaddr`
4. `sudo pip install configparser`



Example usage
-------------

1) Update settings.ini with your configuration

2) Start python server.py

3) In your browser:
```
http://localhost:8080/learnCommand/lampon   #learn command with name lampon
http://localhost:8080/sendCommand/lampon    #send command with name lampon
```
4) Added get temperature from supported devices (like RM2/Pro):
```
http://localhost:8080/getStatus/temperature
```
Returns:
```
{ "temperature": 22.2 } 
```
*required JSON format suites [homebridge-http-temperature](https://github.com/metbosch/homebridge-http-temperature) plugin.

5) Added support for A1 sensors (temperature, lights and etc..)
```
http://localhost:8080/a1/temperature
http://localhost:8080/a1/lights
http://localhost:8080/a1/noise
and etc..
```
Returns:
```
{ "temperature": 22.2 } 
{ "lights": dark } 
{ "noise": low } 
and etc..
```
*required JSON format suites [homebridge-http-temperature](https://github.com/metbosch/homebridge-http-temperature) plugin.

6) Get and Set status of devices having COMMANDon and COMMANDoff abilities
```
http://localhost:8080/sendCommand/lampon #automaticly set status of "lamp" to "on"
http://localhost:8080/getStatus/lamp     #return lamp status as 0 or 1
```

7) Added support for SP2 smart plugs 

```

http://localhost:8080/sp2/"IP"/"MAC"/"MODE"

http://localhost:8080/sp2/10.0.0.12/B44300000000/1   # Turn ON SP2 Plug
http://localhost:8080/sp2/10.0.0.12/B44300000000/0   # Turn OFF SP2 Plug

```
