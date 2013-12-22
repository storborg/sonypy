import socket
import re
import requests


from .camera import Camera


SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900
SSDP_MX = 1


discovery_msg = ('M-SEARCH * HTTP/1.1\r\n'
                 'HOST: %s:%d\r\n'
                 'MAN: "ssdp:discover"\r\n'
                 'MX: %d\r\n'
                 'ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n'
                 '\r\n')


dd_regex = ('<av:X_ScalarWebAPI_Service>'
            '\s*'
            '<av:X_ScalarWebAPI_ServiceType>'
            '(.+)'
            '</av:X_ScalarWebAPI_ServiceType>'
            '<av:X_ScalarWebAPI_ActionList_URL>'
            '(.+)'
            '</av:X_ScalarWebAPI_ActionList_URL>'
            '\s*'
            '</av:X_ScalarWebAPI_Service>')


class Discoverer(object):
    camera_class = Camera

    def _interface_addresses(family=socket.AF_INET):
        for info in socket.getaddrinfo('', None):
            if family == info[0]:
                addr = info[-1]
                yield addr

    def _parse_ssdp_response(self, data):
        lines = data.split('\n')
        assert lines[0] == 'HTTP/1.1 200 OK'
        headers = {}
        for line in lines[1:]:
            key, val = line.split(': ', 1)
            headers[key.lower()] = val
        return headers

    def _ssdp_discover(self, timeout=1):
        socket.setdefaulttimeout(timeout)

        for addr in self._interface_addresses():
            sock = socket.socket(socket.AF_INET,
                                 socket.SOCK_DGRAM,
                                 socket.IPPROTO_UDP)
            sock.setstockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR,
                             1)
            sock.setsockopt(socket.IPPROTO_IP,
                            socket.IP_MULTICAST_TTL,
                            2)
            sock.bind((addr, 0))

            for _ in xrange(2):
                msg = discovery_msg % (SSDP_ADDR, SSDP_PORT, SSDP_MX)
                sock.sendto(msg, (SSDP_ADDR, SSDP_PORT))

            try:
                data = sock.recv(1024)
            except socket.timeout:
                pass
            else:
                print "*****"
                print data
                yield self._parse_ssdp_response(data)

    def _parse_device_definition(self, doc):
        """
        Parse the XML device definition file.
        """
        services = {}
        for m in re.findall(dd_regex, doc):
            service_name = m.group(1)
            endpoint = m.group(2)
            services[service_name] = endpoint
        return services

    def _read_device_definition(self, url):
        """
        Fetch and parse the device definition, and extract the URL endpoint for
        the camera API service.
        """
        r = requests.get(url)
        services = self._parse_device_definition(r.text)
        return services['camera']

    def discover(self):
        endpoints = []
        for resp in self._ssdp_discover():
            url = resp['location']
            endpoint = self._read_device_definition(url)
            endpoints.append(endpoint)
        return [self.camera_class(endpoint) for endpoint in endpoints]
