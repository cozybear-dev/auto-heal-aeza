import requests
import json
import os
import logging
import socket

class aeza(object):
    GET_SERVICES    = "https://core.aeza.net/api/services?offset=0&count=100&sort="
    REBOOT_SERVICE  = "https://core.aeza.net/api/services/{id}/ctl?"

    def __init__(self, key):
        self.key    = key
        self.auth_header        = {"X-API-Key": key}
        self.content_header     = {"Content-Type": "application/json"}

    def get_services(self):
        url = self.GET_SERVICES
        headers = {**self.auth_header, **self.content_header}

        resp = requests.get(url=url, headers=headers)
        j = json.loads(resp.content)

        return j

    def reboot_service(self, service_id):
        url = self.REBOOT_SERVICE.format(id=service_id)
        headers = {**self.auth_header, **self.content_header}
        data    = json.dumps({"action": "reboot"})

        resp = requests.post(url=url, headers=headers, data=data)
        j = json.loads(resp.content)

        return j

def get_hostname_with_id(services):
    services_map = {}

    for service in services["data"]["items"]:
        if service["id"] is not None:
            services_map[service["ips"][0]["domain"]] = service["id"]
    
    return services_map

# Credits to @Fmstrat; https://raw.githubusercontent.com/Fmstrat/server-monitor/master/server-monitor.py
def tcpCheck(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

def sendExecutionHeartbeat(heartbeat):
    requests.get(heartbeat)

def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    api = aeza(os.getenv('AEZA_API_KEY'))

    services = get_hostname_with_id(api.get_services())

    logging.info(f'Found the following services: {services}')

    for service in services: #not async fine for now
        if tcpCheck(service, 443) is False:
            logging.critical(f'{service} is down, rebooting now...')
            api.reboot_service(services[service])

    sendExecutionHeartbeat(os.getenv('HEALTH_CHECK_URL'))

if __name__ == '__main__':
    main()