from unitparser import join_unitlist, chunks, parse_imei
from httplib2 import Http
from base64 import b64encode
from datetime import datetime
import json, re, time, csv

BASE_URL = 'https://explore.delorme.com/IPCInbound/V1'

HEN = {
        'user': 'henrico_ipc_api',
        'pass': 'P@55w0rd!'
    }
VDE = {
    'user': "vdem_ipc_api",
    'pass': "DeLorme8707",
}
RAA = {
    'user': "raaems_ipc_inbound",
    'pass': "DeLorme8707",
}
RFD = {
    'user': "rfd_ipc_api",
    'pass': "DeLorme8707",
}
CREDENTIALS = {
    'hen': HEN,
    'vde': VDE,
    'raa': RAA,
    'rfd': RFD,
}

def get_credentials(unit):
    # returns the proper credentials dict for a unit
    reHen = re.compile("hen.*", flags=re.IGNORECASE)
    reRic = re.compile("rfd.*", flags=re.IGNORECASE)
    reRaa = re.compile("raa.*", flags=re.IGNORECASE)
    reVde = re.compile("vde.*", flags=re.IGNORECASE)
    if reHen.match(unit['label']):
        return CREDENTIALS['hen']
    if reRic.match(unit['label']):
        return CREDENTIALS['rfd']
    if reRaa.match(unit['label']):
        return CREDENTIALS['raa']
    if reVde.match(unit['label']):
        return CREDENTIALS['vde']
    return None

def get_unitlastknown(unit):
    # performs a lastknown query for a specific unit.
    url = "%s/Location.svc/LastKnownLocation" % BASE_URL
    fullurl = "%s?imei=%s" % (url, unit['imei'])
    creds = get_credentials(unit)
    if not creds:
        return None
    result = json.loads(api_get(fullurl, creds).decode('utf-8'))
    try:
        return result['Locations'][0]['Timestamp']
    except Exception:
        print(creds, result)
        return None

def _parse_unitstoday():
    with open("unitstoday.csv") as csvfile:
        data = {}
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            data[row['unitid']] = row
        return data

def join_unitlastknown():
    # Puts lastknown update time in the unitlist.
    allunits = _parse_unitstoday()
    for id, unit in allunits.items():
        lk = get_unitlastknown(unit)
        if lk:
            unit['LastUpdate'] = _extract_datetime(lk)
    return allunits

def write_unitlastknown():
    fn = "unitlastknown-%s" % time.strftime("%Y%m%d-%H%M%S")
    headers = ['unitid', 'label', 'imei', 'branch', 'LastUpdate']
    with open('%s.csv' % fn, 'w') as csvfile:
        wrtr = csv.DictWriter(csvfile, fieldnames=headers)
        for k, unit in join_unitlastknown().items():
            wrtr.writerow(unit)

# This was group api stuff
# def parse_unitdevices():
#     # breaks a list of units into list groups.
#     allunits = join_unitlist()
#     unitgroups = {
#         'hen': [],
#         'rfd': [],
#         'raa': [],
#         'vde': [],
#     }
#     reHen = re.compile("hen.*", flags=re.IGNORECASE)
#     reRic = re.compile("rfd.*", flags=re.IGNORECASE)
#     reRaa = re.compile("raa.*", flags=re.IGNORECASE)
#     reVde = re.compile("vde.*", flags=re.IGNORECASE)
#     for k, unit in allunits.items():
#         if reHen.match(unit['Delorme']):
#             unitgroups['hen'].append(unit)
#         if reRic.match(unit['Delorme']):
#             unitgroups['rfd'].append(unit)
#         if reRaa.match(unit['Delorme']):
#             unitgroups['raa'].append(unit)
#         if reVde.match(unit['Delorme']):
#             unitgroups['vde'].append(unit)
#     return unitgroups
#
def api_get(url, acnt, params=None):
    #does a simple get request to the api.
    http = Http(disable_ssl_certificate_validation=True)
    http.add_credentials(acnt['user'], acnt['pass'])
    headers = { 'Content-type': 'application/json', }
    resp, content = http.request(url, "GET", headers=headers)
    return content
#
# def get_lastknown(units, k):
#     url = "%s/Location.svc/LastKnownLocation" % BASE_URL
#     imeis = [unit['IMEI'] for unit in units]
#     fullurl = "%s?imei=%s" % (url, ",".join(imeis))
#     result = json.loads(api_get(fullurl, k).decode('utf-8'))
#     data = {}
#     for loc in result['Locations']:
#         data[loc['IMEI']] = loc
#     return data
#
# def update_groups(groups):
#     for key in CREDENTIALS.keys():
#
# def _update_group(unitlist):
#     '''Iterates through the devices in the unit list and gets last update time.'''
#     for unit in unitlist

def _extract_datetime(tsdate):
    datematch = re.compile(r'\/Date\((\d*)\)\/')
    m = datematch.search(tsdate)
    if m:
        msTs = (int(m.group(1)))
        tm = datetime.utcfromtimestamp(msTs / 1e3)
        return tm
    else:
        return None

if __name__ == '__main__':
    write_unitlastknown()
