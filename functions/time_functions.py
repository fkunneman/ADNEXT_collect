
import re
import datetime

def return_date(chars, docdate = False):

    if re.search('-', chars):
        parts = chars.split('-')
    else:
        parts = chars.split('/')
    parts = [int(x) for x in parts]
    if len(parts) == 3:
        if parts[0] > 1000: #first is a year
            year = parts[0]
            month = parts[1]
            day = parts[2]
        else:
            day = parts[0]
            month = parts[1]
            if parts[2] < 100: # length is two
                parts[2] = 2000 + parts[2]
            year = parts[2]
    elif len(parts) == 2:
        if parts[1] > 12:
            day = parts[1]
            month = parts[0]
        else:
            day = parts[0]
            month = parts[1]
        year = datetime.date.today().year
    return datetime.date(year, month, day)

def return_datetime(datestr,timestr = False,minute = False,setting = "eu"):
    """Put a date and time string in the python datetime format."""
    if setting == "eu":            
        parse_date = re.compile(r"(\d{2})-(\d{2})-(\d{4})")
        pds = parse_date.search(datestr).groups()
        date = [pds[2],pds[1],pds[0]]
    elif setting == "vs":
        parse_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
        date = parse_date.search(datestr).groups(1)
    elif setting == "twitter":
        month = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, 
            "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
        parse_dt = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d+) " +
            r"(\d{2}:\d{2}:\d{2}) \+\d+ (\d{4})")
        dtsearch = parse_dt.search(datestr).groups()
        date = [dtsearch[3],month[dtsearch[0]],dtsearch[1]]
        time = dtsearch[2]
    if time:
        parse_time = re.compile(r"^(\d{2}):(\d{2})")
        timeparse = parse_time.search(timestr).groups(1)
        if minute:
            datetime_obj = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(timeparse[0]),0,0)
        else:
            datetime_obj = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(timeparse[0]),int(timeparse[1]),0)
    else:
        datetime_obj = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),0,0,0)
    return datetime_obj

def timerel(time1, time2, unit):
    """Return the difference in time in a given time unit between two datetime objects.""" 
    if unit == "day":
        day = (time1.date() - time2.date()).days
        if day < 0:
            day = day*-1
        return day
    else:
        dif = time1 - time2
        if unit == "hour":
            hours = (int(dif.days) * 24) + (int(dif.seconds) / 3600)
            return hours
        if unit == "minute":   
            minutes = (int(dif.days) * 1440) + int(dif.seconds / 60)
            return minutes

def select_tweets_bda(docs, date_index, time_index, during_begin, during_end, setting = 'eu'):
    """
    Function to distinguish documents posted before, during and after a timeslot (for example an event)

    Parameters
    -----
    docs (list)                             : list of documents, each document is a list of datapoints
    date_index (int)                        : the index in the document that contains the date of creation, of type datetime.date()
    time_index (int)                        : the index in the document that contains the time of creation, of type datetime.time()
    during_begin (datetime.datetime)        : the begin time of the time slot
    during_end (datetime.datetime)          : the end time of the time slot
    setting                                 : the format of the document date

    Returns
    -----
    before (list)                           : list of documents, posted before the timeslot
    during (list)                           : list of documents, posted during the timeslot
    after (list)                            : list of documents, posted after the timeslot    
    """
    before, during, after = [], [], []
    for document in docs:
        try:
            doc_dt = return_datetime(document[date_index], document[time_index], setting = setting)
            if doc_dt < during_begin:
                before.append(document)
            elif doc_dt > during_end:
                after.append(document)
            else: # on same day
                during.append(document)
        except:
            continue
    return before, during, after
