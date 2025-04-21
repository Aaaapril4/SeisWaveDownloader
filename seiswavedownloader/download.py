from obspy.clients.fdsn import Client
from obspy.core.utcdatetime import UTCDateTime
from obspy.clients.fdsn.mass_downloader import Restrictions,MassDownloader

import multiprocessing as mp
from tqdm import tqdm
import calendar

client = Client("IRIS")
mdl = MassDownloader(providers=["IRIS"])

def get_station(para):
    '''
    Get the info of all available networks and stations satisfying requirements
    Return:
        station inventory
    '''

    Netinv = client.get_stations(
        network = para["Station Info"].get("network", "*"),
        station = para["Station Info"].get("station", "*"),
        channel = para["Station Info"].get("channelPriority", "*"),
        starttime = para["Station Info"].get("startTime", "19700101T00:00:00"),
        endtime = para["Station Info"].get("endTime", UTCDateTime.now()),
        maxlatitude = para["Map Info"].getfloat("maxLatitude"),
        minlatitude = para["Map Info"].getfloat("minLatitude"),
        maxlongitude = para["Map Info"].getfloat("maxLongitude"),
        minlongitude = para["Map Info"].getfloat("minLongitude")
    )

    filter_net = para["Station Info"].get("networkFilter").split(",")
    for net in filter_net:
        Netinv = Netinv.remove(network=net)

    if para["Save Data"].getboolean("stationInfo"):
        Netinv.write(f'{para["DEFAULT"].get("dataDir")}/station.txt', format="STATIONTXT", level='station')

    return Netinv



def get_event_radius(minradius, maxradius, minmag, para):
    '''
    Get all the events in time range
    Return:
        Event catalog
    '''
    
    maxlatitude = para["Map Info"].getfloat("maxLatitude")
    minlatitude = para["Map Info"].getfloat("minLatitude")
    maxlongitude = para["Map Info"].getfloat("maxLongitude")
    minlongitude = para["Map Info"].getfloat("minLongitude")
    
    cat = client.get_events(
        starttime=para["Station Info"].get("startTime", "19700101T00:00:00"),
        endtime=para["Station Info"].get("endTime", UTCDateTime.now()),
        latitude=(maxlatitude+minlatitude) / 2,
        longitude=(maxlongitude+minlongitude) / 2,
        minradius=minradius,
        maxradius=maxradius,
        minmagnitude=minmag)

    for event in cat:
        extra = {"downloaded": {"value": "False",
                "namespace":"http://test.org/xmlns/1.0"}}
        event.extra = extra
    
    if para["Save Data"].getboolean("eventCatlog"):
        cat.write(f'{para["DEFAULT"].get("dataDir")}/evcatalog.xml', format="QUAKEML")
    
    return cat



def _get_nettime(nw, para):
    '''
    Calculate the time range of each network for downloading
    Return:
        starttime, endtime
    '''

    nwbegin = min([sta.start_date for sta in nw.stations])
    if None in [sta.end_date for sta in nw.stations]:
        nwend = UTCDateTime.now()
    else:
        nwend = max([sta.end_date for sta in nw.stations])

    return max(nwbegin, UTCDateTime(para["Station Info"].get("startTime"))), min(nwend, UTCDateTime(para["Station Info"].get("endTime")))



def get_nettime(Netinv, para):
    nettime = []
    for nw in Netinv:
        starttime, endtime = _get_nettime(nw, para)
        nettime.append((nw.code, starttime, endtime))
    return nettime



def _get_downloadlist(Netinv, para):
    '''
    Split the network time into several slots for parallal downloading
    Return:
        list of tunnel (networkname, begintime, endtime)
    '''
    try:
        chunksize = int(para["Station Info"].get("chunkSize", 1))
    except ValueError:
        if para["Station Info"].get("chunkSize").lower() != "mon":
            raise ValueError("Chunksize is invalid")
        
        downloadlist = []
        for nw in Netinv:
            starttime, endtime = _get_nettime(nw, para)
            d_begin = UTCDateTime(starttime.year, starttime.month, 1)
            while d_begin < endtime:
                d_end = d_begin + calendar.monthrange(d_begin.year, d_begin.month)[1] * 60 * 60 * 24 - 1e-6
                downloadlist.append((nw.code, d_begin, d_end))
                d_begin = d_end + 1e-6
        
    else:
        downloadlist = []
        for nw in Netinv:
            starttime, endtime = _get_nettime(nw, para)
            downloadlist.append((nw.code, UTCDateTime(starttime.strftime('%Y%m%d')), UTCDateTime(endtime.strftime('%Y%m%d')) + 60*60*24*chunksize))
    
    return downloadlist



def _download_cont(nw, starttime, endtime, para, domain):
    '''
    Download data for each network
    '''
    print(f'======Download data for network {nw}: {starttime} - {endtime}======')
    try:
        chunksize = int(para["Station Info"].get("chunkSize"))
    except ValueError:
        if para["Station Info"].get("chunkSize").lower() != "mon":
            raise ValueError("Chunksize is invalid")

        restrictions = Restrictions(
            starttime = starttime,
            endtime = endtime,
            network = nw,
            station = para["Station Info"].get("station", "*"),
            channel_priorities = para["Station Info"].get("channelPriority", "*").split(","),
            reject_channels_with_gaps = False,
            minimum_length = 0.01,
            minimum_interstation_distance_in_m = 100.0)
        
    else:
        restrictions = Restrictions(
            starttime = starttime,
            endtime = endtime,
            chunklength_in_sec = chunksize * 24 * 60 * 60,
            network = nw,
            station = para["Station Info"].get("station", "*"),
            channel_priorities = para["Station Info"].get("channelPriority", "*").split(","),
            reject_channels_with_gaps = False,
            minimum_length = 0.01,
            minimum_interstation_distance_in_m = 100.0)

    mdl.download(
        domain, 
        restrictions, 
        mseed_storage = para["DEFAULT"].get("dataDir") + "/waveform/{network}.{station}/{network}.{station}.{location}.{channel}__{starttime}__{endtime}.mseed", 
        stationxml_storage = para["DEFAULT"].get("dataDir") + "/station/{network}.{station}.xml")

    return



def download_cont(para, domain):
    '''
    Download continuous waveform for all networks
    '''
    Netinv = get_station(para)
    downloadlist = _get_downloadlist(Netinv, para)
    if para["DEFAULT"].getint("ncpu") == 1:
        for i in range(len(downloadlist)):
            _download_cont(*downloadlist[i], para, domain)
    else:
        with mp.Pool(para["DEFAULT"].getint("ncpu")) as p:
            list(tqdm(p.starmap(_download_cont, [(nw, st, et, para, domain) for nw, st, et in downloadlist]), total=len(downloadlist)))

    return



def _download_event(eventtime, starttime, endtime, para, domain):
    '''
    Download each event for all stations
    '''
    restrictions = Restrictions(
                        starttime = eventtime - starttime,
                        endtime = eventtime + endtime,
                        network = para["Station Info"].get("network", "*"),
                        station = para["Station Info"].get("station", "*"),
                        reject_channels_with_gaps = False,
                        minimum_length = 1.0,
                        channel_priorities = para["Station Info"].get("channelPriority", "*").split(","))

    mdl.download(
        domain, 
        restrictions, 
        mseed_storage = f'{para["DEFAULT"].get("dataDir")}/waveform/{network}.{station}/{network}.{station}.{location}.{channel}__{starttime}__{endtime}.mseed', 
        stationxml_storage = f'{para["DEFAULT"].get("dataDir")}/station/{network}.{station}.xml')
    return



def _download_each_event(event, para, domain):
    '''
    Download one event teleseismic P wave for all stations
    Output:
        None
    '''

    if event.extra['downloaded']['value'] == "False":
            eventtime = event.origins[0].time
            try:
                _download_event(eventtime, para["Event Info"].getint("startTime_sec"), para["Event Info"].getint("endTime_sec"), para, domain)
            except:
                return
            event.extra['downloaded']['value'] = "True"
    
    return event



def download_event(para, domain):
    '''
    Download events for teleseismic P wave
    Output:
        None
    '''

    cat = get_event_radius(para["Event Info"].getfloat("minRadius"), para["Event Info"].getfloat("maxRadius"), para["Event Info"].getfloat("minMagnitude"), para)
    with mp.Pool(para["DEFAULT"].getint("ncpu")) as p:
        cat_list = list(tqdm(p.imap(_download_each_event, [(event, para, domain) for event in cat]), total=len(cat)))
    
    cat_new = cat.copy()
    cat_new.clear()
    for event in cat_list:
        cat_new.append(event)

    return