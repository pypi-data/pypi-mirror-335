import asyncio
import logging
import sys
import threading
import time

sys.path.append("../")
logging.basicConfig(level=20)

from pysmarlaapi import Connection, ConnectionHub
from pysmarlaapi.federwiege import AnalyserService, BabywiegeService

try:
    from config import AUTH_TOKEN_PERSONAL, HOST
except ImportError:
    print("config.py or mandatory variables missing, please add in root folder...")
    exit()

loop = asyncio.get_event_loop()
async_thread = threading.Thread(target=loop.run_forever)

connection = Connection(url=HOST, token_json=AUTH_TOKEN_PERSONAL)

hub = ConnectionHub(loop, connection, interval=10, backoff=0)
babywiege_svc = BabywiegeService(hub)
analyser_svc = AnalyserService(hub)


def main():
    async_thread.start()
    hub.start()

    while not hub.connected:
        time.sleep(1)

    swing_active_prop = babywiege_svc.get_property("swing_active")
    intensity_prop = babywiege_svc.get_property("intensity")
    oscillation_prop = analyser_svc.get_property("oscillation")

    time.sleep(1)

    value = swing_active_prop.get()
    print(f"Swing Active: {value}")
    intensity = intensity_prop.get()
    print(f"Intensity: {intensity}%")
    oscillation = oscillation_prop.get()
    print(f"Amplitude: {oscillation[0]}mm Period: {oscillation[1]}ms")

    swing_active_prop.set(True)
    intensity_prop.set(60)

    time.sleep(1)

    value = swing_active_prop.get()
    print(f"Swing Active: {value}")
    intensity = intensity_prop.get()
    print(f"Intensity: {intensity}%")
    oscillation = oscillation_prop.get()
    print(f"Amplitude: {oscillation[0]}mm Period: {oscillation[1]}ms")

    time.sleep(1)

    while True:
        value = swing_active_prop.get()
        print(f"Swing Active: {value}")
        intensity = intensity_prop.get()
        print(f"Intensity: {intensity}%")
        oscillation = oscillation_prop.get()
        print(f"Amplitude: {oscillation[0]}mm Period: {oscillation[1]}ms")
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        pass
    hub.stop()
    loop.call_soon_threadsafe(loop.stop)
