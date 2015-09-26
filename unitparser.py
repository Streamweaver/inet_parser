#!/usr/bin/env
import csv, time
#import str

class UCIException(Exception):
    pass

def parse_imei(filename):
    # parses the imei csv file and returns a dict of id and imei number
    data = {}
    with open(filename) as csvfile:
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            lbl = _clean(row['Label'])
            if lbl in data:
                raise UCIException
            data[lbl] = row['IMEI']
    return data

def parse_unitlist (filename):
    # parses the unit list sent by planning int a dict of unitid and datadict
    with open(filename) as csvfile:
        data = {}
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            lbl = _clean(row['unitid'])
            if lbl in data:
                raise UCIException
            data[lbl] = {
                'unitid': lbl,
                'Delorme': _clean(row['Delorme']),
                'Branch': row['Branch']
            }
        _chk_duplabel(data)
        return data

def _clean(label):
    # cleans field contents of spaces and normalizes the data.
    lbl = label.upper()
    lbl = str.replace(lbl, " ", "")
    if lbl in ['N/A', 'NA']:
        return None
    return lbl

def _chk_duplabel(unitdata):
    # checks for duplicate delorem lables
    labels = []
    for k, v in unitdata.items():
        if v['Delorme']:
            if v['Delorme'] in labels:
                print("Found duplicate label for %s" % v['Delorme'])
                raise UCIException
            labels.append(v['Delorme'])


def _chk_dupimei(imeidata):
    # checks for duplicate imeis
    imeis = []
    for k, v in imeidata.items():
        if v['IMEI'] in imeis:
            print("Found duplicate imei %s" % v)
            raise UCIException
        labels.append(v['IMEI'])

def xrange(x):
    return iter(range(x))

def chunks(MyList, n):
    # chunks arrays
    chunk = []
    chunks = []
    for x in range(0, len(MyList), n):
        chunk = MyList[x:x+n]
        chunks.append(chunk)
    return chunks

def join_unitlist():
    #writes a joined unit list to edit in inet
    devices = parse_imei("imei.csv")
    units = parse_unitlist("unitlist.csv")
    for id, unit in units.items():
        if unit['Delorme']:
            unit['IMEI'] = devices.get(unit['Delorme'], None)
    return units

def write_joinedunitlist(units):
    #writes the a joined unit list to csv
    fn = "units-%s" % time.strftime("%Y%m%d-%H%M%S")
    with open('%s.csv' % fn, 'w') as csvfile:
        headers = ['unitid', 'Delorme', 'IMEI', 'Branch']
        wrtr = csv.DictWriter(csvfile, fieldnames=headers)
        for id, unit in units.items():
            if unit['Delorme']:
                wrtr.writerow(unit)

def join_activationlist():
    units = parse_unitlist("unitlist.csv")
    active_units = [k for k, v in units.items() if v['Branch'] or v['Delorme']]
    unit_chunks = chunks(active_units, 5)
    fn = "activate-%s" % time.strftime("%Y%m%d-%H%M%S")
    with open('%s.txt' % fn, 'w') as f:
        for chunk in unit_chunks:
            f.write(" ".join(chunk).lower() + " lo\n")

def join_deactivationlist():
    units = parse_unitlist("unitlist.csv")
    active_units = [k for k, v in units.items() if v['Branch'] or v['Delorme']]
    unit_chunks = chunks(active_units, 5)
    fn = "deactivate-%s" % time.strftime("%Y%m%d-%H%M%S")
    with open('%s.txt' % fn, 'w') as f:
        for chunk in unit_chunks:
            f.write(" ".join(chunk).lower() + " loff\n")

if __name__ == '__main__':
    write_joinedunitlist(join_unitlist())
    join_activationlist()
    join_deactivationlist()
