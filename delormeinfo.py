from dataparser import join_unitlist, chunks
from httplib2 import Http
from base64 import b64encode
import json

BASE_URL = 'https://explore.delorme.com/IPCInbound/V1'

HEN = {
        'user': 'henrico_ipc_api',
        'pass': 'P@55w0rd!'
    }
VDE = {
    'user': "vdem_ipc_api",
    'pass': "DeLorme8707"
}
RAA = {
    'user': "raaems_ipc_inbound",
    'pass': "DeLorme8707,"
}
RFD = {
    'user': "rfd_ipc_api",
    'pass': "DeLorme8707,"
}
CREDENTIALS = {
    'hen': HEN,
    'vde': VDE,
    'raa': RAA,
    'rfd': RFD,
}

def get_units():
    # breaks a list of units into list groups.
    allunits = join_unitlist()
    unitgroups = {
        'hen': [],
        'ric': [],
        'raa': [],
        'vde': [],
    }
    for k, unit in allunits.items():
        key = unit['Delorme'][0:3] if len(unit['Delorme']) > 2 else 'no'
        group = unitgroups.get(key.lower(), "skip")
        if group != "skip":
            group.append(unit)
    return unitgroups

def api_get(url, acnt, params=None):
    #does a simple get request to the api.
    http = Http(disable_ssl_certificate_validation=True)
    http.add_credentials(acnt['user'], acnt['pass'])
    headers = { 'Content-type': 'application/json', }
    resp, content = http.request(url, "GET", headers=headers)
    return content

def get_lastknown():
    url = "%s/Location.svc/LastKnownLocation" % BASE_URL
    groups = get_units()
    content = []
    for k, group in groups.items():
        for chunk in chunks(group, 10):
            imeis = [u['Delorme'] for u in chunk if u['Delorme']]
            fullurl = "%s?imei=%s" % (url, ",".join(imeis))
            rtrn = json.loads(api_get(fullurl, CREDENTIALS.get(k)).decode('utf-8'))
            print(rtrn)
            #content.extend(rtrn['Locations'])
    return content

if __name__ == '__main__':
    print('%r' % get_lastknown())
