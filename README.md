# tado_aa (Tado Auto-Assist for Geofencing and Open Window Detection)

**This project is obsolete due to the API limitations for free users of tado.**  
**Checkout my new project [tado-automate-web](https://github.com/mzettwitz/tado-automate-web) to bypass this limitations.**

---

A python script that automatically adjusts the temperature in your home at leaving or arriving (if geofencing is enabled) based on your settings from tado app and automatically switch off the heating (activating Open Window Mode) in the room where tado TRV detects an open window. The script is adjusted for use with docker. Hence. ´USERNAME´, ´PASSWORD´, and ´GEOFENCING´ are set in environment variables.

Requires PyTado: `$ pip3 install python-tado`
This script was possible because of PyTado author, Chris Jewell (chrism0dwk@gmail.com) and the person who modified it, Wolfgang Malgadey (wolfgang@malgadey.de).

#### If you want to support the original author
[Paypal](https://paypal.me/adrianslabu)

### For docker use:
Build with `docker build -t tado_aa_geo .` and run docker from console `docker run --name tado_aa_container --restart always -e GEOFENCING=False tado_aa_geo:latest`.  
Alternatively, use docker-compose `docker compose up -d` Don't forget to set the environment variables in compose.yml.

You are prompted to login at your tado account the first time, to authenticate your device. Enter the link in the console output. The auth token will be stored inside your container.
