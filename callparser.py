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
_eventsummaryheaders = ["Event Number","Create Date","Closed Date","Status",
    "Event Type","UnitID:","Location","Phone","Surname:","Firstname:"]
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
            row.pop('', None)
            if row['Event ID']:
                data[row['Event ID']] = row
    return data

def _is_badevent(event):
    # parses a dict from a summary event row to see if it's test or cancelled
    bad = False
    tests = [
        re.compile(r".*\bTEST\b.*", flags=re.IGNORECASE),
        re.compile(r".*\bCANCELLED\b.*", flags=re.IGNORECASE),
        re.compile(r".*\bLINKEDCANCELLED\b.*", flags=re.IGNORECASE),
    ]
    for test in tests:
        if test.search(event['Status']) or test.search(event['Event Type']):
            bad = True
    return bad

def parse_badcalls():
    # Returns a list of event ids that are know to be test or cancelled
    data = []
    with open("FullEventSummary.csv") as csvfile:
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            row.pop('', None)
            if _is_badevent(row) and row['Event Number']:
                data.append(row['Event Number'])
    return data

def parse_eventsummary(filename):
    # Parse the event summary list to remove bad calls
    data = {}
    with open(filename) as csvfile:
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            row.pop('', None)
            if row['Event Number'] and not _is_badevent(row):
                data[row['Event Number']] = row
    data.pop('', None)
    return data

def parse_unitaffiliation(filename):
    # Parses the Unit Affiliation list.
    data = {}
    with open(filename) as csvfile:
        rdr = csv.DictReader(csvfile)
        for row in rdr:
            data[row['UNITID']] = row
    return data

def set_jurisdiction():
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

def write_eventsummary():
    data = parse_eventsummary('EventSummary.csv')
    fn = "eventsummary-%s" % time.strftime("%Y%m%d-%H%M%S")
    with open("%s.csv" % fn, "w") as csvfile:
        wrtr = csv.DictWriter(csvfile, fieldnames=_eventsummaryheaders)
        wrtr.writeheader()
        for k, event in data.items():
            if event["Event Number"] and not _is_badevent(event):
                wrtr.writerow(event)

def write_cleanedeventdetails():
    badcalls = parse_badcalls()
    events = set_jurisdiction()
    fn = "eventdetails-%s" % time.strftime("%Y%m%d-%H%M%S")
    with open("%s.csv" % fn, "w") as csvfile:
        wrtr = csv.DictWriter(csvfile, fieldnames=_eventdetailheaders)
        wrtr.writeheader()
        for k, event in events.items():
            if event['Event ID'] not in badcalls:
                wrtr.writerow(event)

if __name__ == '__main__':
    write_cleanedeventdetails()
    write_eventsummary()
    print(parse_unitaffiliation("UnitAffiliation.csv"))
