#!/usr/bin/env
import csv, time, re

_eventdetailheaders = ["Event ID","UCI","Event Type","","Location","Zone",
                        "Agency Create Method","Answer To Agency Event",
                        "Answer To Dispatch Unit","Answer To Onscene",
                        "Answer To Close","Agency Event To Dispatch Unit",
                        "Agency Event To Onscene","Agency Event To Close",
                        "CAD Position#","Primary Unit","Primary Unit Employee",
                        "Answering Employee","Answering Device ID",
                        "Disposition","Create Date","Event Source","X","Y",
                        "Community"
                        ]

def parse_dispatchgroups(filename):
    # parses the dispatch groups into a branch jurisdiction key value set.
    data = {}
    with open(filename) as csvfile:
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            data[row['Branch'].lower()] = row['Jurisdiction']
    return data

def parse_detailedinfo(filename):
    # parses the eventdetailedinformation csv file into a dict.
    data = {}
    with open(filename) as csvfile:
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            if row['Event ID']:
                data[row['Event ID']] = row
    return data

def parse_badcalls():
    data = []
    tests = [
        re.compile(r".*\bTEST\b.*", flags=re.IGNORECASE),
        re.compile(r".*\bCANCELLED\b.*", flags=re.IGNORECASE),
        re.compile(r".*\bLINKEDCANCELLED\b.*", flags=re.IGNORECASE),
    ]
    with open("FullEventSummary.csv") as csvfile:
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            good = True
            for test in tests:
                if test.search(row['Status']) or test.search(row['Event Type']):
                    good = False
            if not good and row['Event Number']:
                data.append(row['Event Number'])
    return data

def parse_eventsummary(filename):
    # Parse the event summary list to remove bad calls
    badcalls = parse_badcalls()
    data = []
    with open(filename) as csvfile:
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            if row['Event ID'] not in badcalls:
                data.append(row)
    return data

def count_jurisdiction():
    events = parse_detailedinfo("EventDetailedInformation.csv")
    groups = parse_dispatchgroups("dispatchgroups.csv")
    regions = set([group for k, group in groups.items()])
    for k, event in events.items():
        if not event['Community'] or event['Community'] not in regions:
            zone = event.get('Zone', 'na')
            event['Community'] = 'unknown'
            if zone.lower() in groups:
                event['Community'] = groups[zone.lower()]
    return events

def write_cleanedeventdetails():
    badcalls = parse_badcalls()
    events = count_jurisdiction()
    fn = "eventdetails-%s" % time.strftime("%Y%m%d-%H%M%S")
    with open("%s.csv" % fn, "w") as csvfile:
        wrtr = csv.DictWriter(csvfile, fieldnames=_eventdetailheaders)
        wrtr.writeheader()
        for k, event in events.items():
            if event['Event Number'] not in badcalls:
                wrtr.writerow(event)

if __name__ == '__main__':
    write_cleanedeventdetails()
    print(len(parse_eventsummary('FullEventSummary.csv')))
