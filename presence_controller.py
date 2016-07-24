import httplib
import base64
import time
from datetime import datetime


class PresenceController:
    def __init__(self, router_host, router_uri, router_username, router_password, monitored_mac_addresses,
                 search_prefix_for_mac, search_suffix_for_mac):
        self._router_host = router_host
        self._router_uri = router_uri
        self._router_username = router_username
        self._router_password = router_password
        self._search_prefix_for_mac = search_prefix_for_mac
        self._search_suffix_for_mac = search_suffix_for_mac

        # dict MAC address -> last seen timestamp
        self._monitored_mac_addresses = dict(zip(monitored_mac_addresses,
                                                 [datetime.fromtimestamp(0)]*len(monitored_mac_addresses)))

    def _check_connected_devices(self):
        # base64 encode the username and password
        auth = base64.encodestring('%s:%s' % (self._router_username, self._router_password)).replace('\n', '')

        webservice = httplib.HTTPConnection(self._router_host, timeout=60)
        # write your headers
        webservice.putrequest("GET", self._router_uri)
        webservice.putheader("Host", self._router_host)
        webservice.putheader("User-Agent", "NEXA-Controller")
        webservice.putheader("Content-type", "text/html; charset=\"UTF-8\"")
        webservice.putheader("Content-length", "0")
        # write the Authorization header like: 'Basic base64encode(username + ':' + password)
        webservice.putheader("Authorization", "Basic %s" % auth)

        webservice.endheaders()
        # get the response
        response = webservice.getresponse()
        if response.status != 200:
            raise Exception("Can't connect to router: " + response.reason)

        router_web_page = response.read()
        for device in self._monitored_mac_addresses.keys():
            search_for_message = self._search_prefix_for_mac + device + self._search_suffix_for_mac
            if search_for_message in router_web_page:
                self._monitored_mac_addresses[device] = datetime.now()

    def dispatch(self):
        successful_result = False
        while not successful_result:
            try:
                self._check_connected_devices()
                successful_result = True
            except Exception as e:
                print str(e)
                print "Sleeping 60 seconds..."
                time.sleep(60)

        current_time = datetime.now()
        for device in self._monitored_mac_addresses.keys():
            time_diff = current_time - self._monitored_mac_addresses[device]
            if time_diff.total_seconds() < 5*60:
                return True

        print "PresenceController: No devices from the list are alive for the last 5 minutes, disabling:" +\
              str(self._monitored_mac_addresses)
        return False
