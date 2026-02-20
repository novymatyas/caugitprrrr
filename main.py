import network
import urequests
import time
import json
from lcd_display import init, clear, set_cursor, print_line

IP_API = "http://ip-api.com/json"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---------- LOAD CONFIG ----------
try:
    with open("config.json") as f:
        config = json.load(f)
        SSID = config["wifi_ssid"]
        PASSWORD = config["wifi_password"]
        API_KEY = config["api_key"]
except:
    raise SystemExit("Config error")

# ---------- LCD INIT ----------
init()
clear()
print_line("Booting...")

# ---------- WIFI FUNCTION ----------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        clear()
        print_line("Connecting WiFi")
        wlan.connect(SSID, PASSWORD)

        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    return wlan

wlan = connect_wifi()

if not wlan.isconnected():
    clear()
    print_line("WiFi Failed")
    time.sleep(3)
    raise SystemExit

clear()
print_line("WiFi Connected")
time.sleep(2)

# ---------- GET LOCATION ----------
try:
    r = urequests.get(IP_API)
    loc = r.json()
    r.close()

    lat = loc.get("lat")
    lon = loc.get("lon")

except:
    clear()
    print_line("Location Err")
    time.sleep(3)
    raise SystemExit

# ---------- MAIN LOOP ----------
while True:

    if not wlan.isconnected():
        wlan = connect_wifi()
        if not wlan.isconnected():
            clear()
            print_line("WiFi Lost")
            time.sleep(10)
            continue

    try:
        url = "{}?lat={}&lon={}&units=metric&appid={}".format(
            WEATHER_URL, lat, lon, API_KEY
        )

        r = urequests.get(url)
        data = r.json()
        r.close()

        if str(data.get("cod")) != "200":
            raise Exception("API error")

        temp = round(data["main"]["temp"], 1)
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"]

        clear()
        print_line("T:{}C H:{}%".format(temp, humidity))
        set_cursor(0, 1)
        print_line(desc[:16])

    except:
        clear()
        print_line("Weather Error")

    time.sleep(600)  # 10 minut