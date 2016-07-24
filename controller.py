import sched
import time
import os
from datetime import datetime
from switch_nexa import NexaSwitcher
from time_controller import TimeController
from presence_controller import PresenceController
from kodi_play_pause import KodiPlayPause
from controller_config import Config
from datadog_stat import DataDogStat


def dispatch_all_controllers(sc, controllers, global_status):
    try:
        new_status = True
        for controller in controllers:
            if not controller.dispatch():
                new_status = False
                break

        if global_status is None or global_status != new_status:
            kodi = None
            if Config.KODI_ADDR is not None and len(Config.KODI_ADDR) > 0:
                kodi = KodiPlayPause()
                kodi.pause()
                time.sleep(1)

            print str(datetime.now()) + " Changing status from " + str(global_status) + " to " + str(new_status)
            os.nice(+40)
            for transmitter_code in Config.TRANSMITTER_CODES:
                switcher = NexaSwitcher(Config.RASPBERRY_PI_DATA_PIN, transmitter_code)
                switcher.switch(new_status)
                time.sleep(1)
            os.nice(-40)

            if kodi is not None:
                kodi.play()

            global_status = new_status

        if Config.DATADOG_API_KEY is not None and len(Config.DATADOG_API_KEY) > 0:
            datadog = DataDogStat()
            datadog.post_status(new_status)

    except Exception as e:
        print "Exception: " + str(e)

    sc.enter(60, 1, dispatch_all_controllers, (sc, controllers, global_status))


global_status = None
controllers = [TimeController(),
               PresenceController(Config.ROUTER_HOST,
                                  Config.ROUTER_URI,
                                  Config.ROUTER_USERNAME,
                                  Config.ROUTER_PASSWORD,
                                  Config.MONITORED_MAC_ADRESSES,
                                  Config.SEARCH_PREFIX_FOR_MAC,
                                  Config.SEARCH_SUFFIX_FOR_MAC)]
s = sched.scheduler(time.time, time.sleep)
s.enter(1, 1, dispatch_all_controllers, (s, controllers, global_status))
s.run()
