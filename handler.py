#!/usr/bin/env python
# -*- coding=utf-8 -*-

import queue
import time
import datetime
from functools import partial
from collections import namedtuple
import icabbi
import traceback
import sys

from pydroid import SCGps
from pydroid import SpeechtoText

import globals

class Globals:
    queue = queue.Queue()
    zones = {}
    zoneids = {}
    gps = SCGps()
    droid_speech2txt = SpeechtoText()


# Message event constants.
# used to identify the event type in the message callback. Below will contain properties of that particular
# event type. The object passed into the callback is a namedtuple. Compare the event property with
# one of the EVENT conststants below to determine the event type.
#
# event         - EVENT_QUIT
# None
#
# event         - EVENT_CHECK_STATUS
# enable        - bool
#
# event         - EVENT_DRIVER_UPDATE
# driver_id     - integer
#
# event         - EVENT_HOST_UPDATE
# host          - string
#
# event         - EVENT_PREBOOKINGS_UPDATE
# prebookings   - list
#
# event         - EVENT_ZONE_UPDATE
# driver        - dict
# zone          - dict
#
# event         - EVENT_BID_UPDATE
# bid           - dict {"title": str, "id": str, "distance": float, "bid_on_job": bool}
#
# event         - EVENT_NEW_JOB
# driver        - dict
# booking       - dict
#
# event         - EVENT_LOGGED_OUT
# None
#
# event         - EVENT_JOB_OFFER
# accepted      - bool
# offer         - dict
#
# event         - EVENT_BOOKING_UPDATE
# status        - integer
#
# event         - EVENT_NETWORK_ERROR
# message       - string
#
# event         - EVENT_BOOKING_ARCHIVE
# offsets       - list of offset strings. determine how many bookings to retrieve each offset is incremented by 100
#                 example: last 300 bookings offsets = ["0", "100", "200"]
# bookings      - list
#
# event         - EVENT_DEBUG_MODE
# enable        - bool
# message       - string
#
# event         - EVENT_PAUSE_THREAD
# enable        - bool
#
#
# event             - EVENT_KICK_DRIVERS
# drivers           - list
# driver_kick_count - int
# message           - str
EVENT_QUIT = 1001
EVENT_CHECK_STATUS = 1002
EVENT_DRIVER_UPDATE = 1003
EVENT_HOST_UPDATE = 1004
EVENT_PREBOOKINGS_UPDATE = 1005
EVENT_ZONE_UPDATE = 1006
EVENT_BID_UPDATE = 1007
EVENT_NEW_JOB = 1008
EVENT_LOGGED_OUT = 1009
EVENT_JOB_OFFER = 1010
EVENT_BOOKING_UPDATE = 1011
EVENT_NETWORK_ERROR = 1012
EVENT_BOOKING_ARCHIVE = 1013
EVENT_CHANGE_BIDDING = 1014
EVENT_PAUSE_THREAD = 1015
EVENT_KICK_DRIVERS = 1016
EVENT_MESSAGE_ARCHIVE = 1017
EVENT_MESSAGE = 1018
EVENT_MESSAGE_DISPATCH = 1019
EVENT_ZONES = 1020
EVENT_ANDROID_START_GPS = 1021
EVENT_THREAD_EXCEPTION = 1022

def _new_default_zone():
    """ creates a new zone dictionary """
    return dict({"title": "", "total": "0", "id": "0", "position": "0", "status": "", "job_count": "0"})


def _new_default_states():
    """ creates a new saved state dictionary """
    return dict({"status": 4, "zone": _new_default_zone(), "booking_ids": []})


def _check_job_offers(_driver, _host):
    """ 
    Checks for any job offers found in the driver dictionary and applies for the job offer

    returns the job offer dictionary if successful or returns None
    """
    if "offers" in _driver:
        job_offer = _driver["offers"][0]
        icabbi.reply2joboffer(_driver["id"], _host, job_offer["id"], "ACCEPTED")
        return job_offer
    elif "offer" in _driver:
        job_offer = _driver["offer"]
        icabbi.reply2joboffer(_driver["id"], _host, job_offer["id"], "ACCEPTED")
        return job_offer
    else:
        return None


def add_to_takings(takings, booking):
    """
    increments the takings dictionary
    """
    payment = booking["payment"]
    meter = float(payment["meter"])
    extra = float(payment["extras"])
    takings["meter"] += meter
    takings["extra"] += extra
    takings["gross"] += meter + extra
    if booking["account_type"].upper() == "CASH":
        takings["cash"] += meter
        takings["cash"] += extra
    elif booking["account_type"].upper() == "CARD":
        takings["card"] += meter
        takings["card"] += extra
    else:
        takings["account"] += meter
        takings["account"] += extra


def _check_prebookings(driverid, host, booking_ids):
    """ checks for any new pre-booking entries from the icabbi database """
    prebookings = icabbi.getprebookings(driverid, host)
    def prebooking_not_exist(prebooking): 
        return prebooking["id"] not in booking_ids
    new_prebookings = list(filter(prebooking_not_exist, prebookings))
    return new_prebookings


def _has_zone_changed(driver, host, previous_zone):
    """ 
    checks if zone has changed or properties have been altered. Returns zone dictionary if change has occured.

    Returns None if no changes have occured
    current_zone:
        position:           int
        title:              str
        ext_zone_info       dict
    """
    # a little annoying- the driver zone dictionary does not contain a job count property
    # so it requires a call to getzones to obtain a list of zones with job_count
    # this is why filter function is used to loop through the zones list and find
    # the zone the driver is on
    try:
        zones = icabbi.getzones(driver["id"], host)
        for zone in iter(zones):
            _zone = icabbi.findzonebyid(Globals.zoneids, zone['id'])
            if _zone:
                zone["name"] = _zone["title"]
            else:
                zone["name"] = "Unknown"
        driver_zone = driver["zones"][0]
        # zone["id"] returned from getzones is the same value as driver["zones"][0]["zone_id"]
        # why icabbi couldnt be consistant i'll never know!!

        def find_driver_zone(zone): 
            return int(zone["id"]) == int(driver_zone["zone_id"])
        # find the drivers zone by looking for a zone id match. May raise IndexError exception
        current_zones = list(filter(find_driver_zone, zones))
        if len(current_zones) > 0:
            current_zone = current_zones[0]
            # compare the previous zone with the current zone the driver is on
            if int(previous_zone["id"]) == int(current_zone["id"]):
                # driver is on the same plot as before check for job count change
                previous_zone_jobcount = int(previous_zone.get("job_count", "0"))
                current_zone_jobcount = int(current_zone.get("job_count", "0"))
                if previous_zone_jobcount == current_zone_jobcount:
                    # job count has not changed return nothing
                    return (None, zones)
            # make sure to add position and zone title to the returning dict.
            current_zone["position"] = driver_zone["position"]
            current_zone["title"] = driver_zone["title"]
            # get extra zone information
            ext_zone_info = icabbi.getzone(driver["id"], host, current_zone["id"])
            if "drivers" in ext_zone_info:
                current_zone["ext_zone_info"] = ext_zone_info
        else:
            current_zone = None
    except KeyError:
        current_zone = None
    return (current_zone, zones)


def _kick_drivers(driver, host, func_callback):
    zone = icabbi.getzone(driver["id"], host, driver["zones"][0]["zone_id"])
    drivers = zone.get("drivers", [])
    driver_position = int(driver["zones"][0]["position"])
    if drivers:
        for _driver in drivers:
            if int(driver["id"]) != int(_driver["id"]):
                if int(_driver["status"]) == 1:
                    if int(_driver["position"]) < driver_position:
                        msg = "kicking {} from queue".format(_driver["name"])
                        func_callback(event=EVENT_KICK_DRIVERS, message=msg)
                        icabbi.getstatus(_driver["id"], host, 0.0, 0.0)
                        func_callback(event=EVENT_KICK_DRIVERS, message=_driver["name"])


def smart_bidding(bidding_zones, driver_coords, settings):
    """
    smart_bidding(bidding_zones, driver_coords, settings) -> dict

    returns a bid dictionary if successful else returns empty dictionary

    parameters:
        bidding_zones       - dict
        driver_coords       - tuple (float)
        settings            - dict
    """
    shortest_distance_bid = {}
    globals.dump_to_file("Bids Availible \n------------------------")
    for bid in bidding_zones:
        # Get the distance in miles between the Driver and Zone location
        zone_coords = (bid["lat"], bid["lng"])
        distance_miles = icabbi.getdistance(driver_coords, zone_coords)
        bid["distance"] = distance_miles
        # check if this is the first iteration
        if "distance" not in shortest_distance_bid:
            shortest_distance_bid = bid
        else:
            # is current bid distance less than the stored bid distance
            if bid["distance"] < shortest_distance_bid["distance"]:
                # store the current bid distance as the shortest so far
                shortest_distance_bid = bid
        globals.dump_to_file("Bid: {} - {}".format(bid["title"], bid["distance"]))
    globals.dump_to_file("--------------------------------- \n \n")
    # if radius is set to 0 then bid irrelevant of distance
    if settings["bidding_radius"] == 0.0:
        return shortest_distance_bid
    else:
        # if shortest bid found is less than max bid distance set then bid on this job
        if shortest_distance_bid["distance"] < settings["bidding_radius"]:
            return shortest_distance_bid
    return {}


def sort_weekly_earnings(bookings):
    def next_booking(booking):
        if float(booking["pickup_date"]) > utc_week_start:
            if booking.get("finish_status") == "COMPLETED":
                add_to_takings(takings, booking)
    takings = { "meter": 0.0, 
                "extra": 0.0, 
                "cash": 0.0, 
                "account": 0.0, 
                "card": 0.0, 
                "gross": 0.0,
                "commission": 0.0,
                "commission_vat": 0.0,
                "net": 0.0}
    utc_week_start = icabbi.get_start_week_utc(datetime.datetime.now())
    list(map(next_booking, bookings))
    return takings

def sort_prebookings(driverid, host, zones):
    """
    retrieves prebookings and sorts and adds them to the zones list
    """
    prebookings = icabbi.getprebookings(driverid, host)
    for prebooking in prebookings:
        # check for zone with prebookings and add the pickup time to the zone
        for zone in zones:
            if zone["id"] == prebooking["zone"]["id"]:
                zone["pickup_date"] = prebooking["pickup_date"]
                prebooking["zone_found"] = True
        #if prebooking.get("zone_found", False) == False:
            ## No id match so append prebooking to zones list
            #zones.append({"id": prebooking["zone"]["id"],
                          #"job_count": 1,
                          #"total": 0,
                          #"stats": "~3",
                          #"name": prebooking["zone"]["title"],
                          #"pickup_date": prebooking["pickup_date"]})
    return zones

def thread_handler(**kwargs):
    """
    thread_handler(**kwargs) --> boolean
    Description: the main event handler interfaces with the icabbi API and a UI.

                Deals with the drivers status bids on jobs. Gives updates on pre bookings
                and also manipulates the drivers gps coordinates on the icabbi server
    kwargs:
        driverid  -- driver id to use. this can be changed by sending EVENT_DRIVER with driver_id
        host      -- assign the host address either use UK6, UK7 from icabbi.py or http://localhost:5000 for debugging.
                     to change the host-- send EVENT_HOST message
        callback  -- the function callback to recieve event messages. Set to _demo_callback by default.
    """
    # hold loop variable states
    previous_state = _new_default_states()
    # driver id state
    driver_id = kwargs.get("driverid", "20020")
    # set local variable driver init
    driver = {}
    # icabbi host state. Uses local server as default
    host = kwargs.get("host", "http://127.0.0.1:5000")
    # shorthand call to callback thread
    dispatch_event = partial(_dispatch_event, callback=kwargs["callback"])
    # dont't check driver status on start up. send EVENT_CHECK_STATUS with status argument set to true
    check_status = False
    # pause condition
    pause_thread = False
    # Latitude and Longitude coordinates. Note only used using Android. Default is set at castle meadow
    latitude = 52.644699
    longitude = 1.282040

    settings = globals.Globals.settings

    try:
        while True:
            icabbi.verbose_mode = settings["icabbi_verbose_mode"]
            try:
                message = Globals.queue.get(timeout=3)
                # EXIT THREAD
                if message.event == EVENT_QUIT:
                    break
                # PAUSE THE THREAD
                elif message.event == EVENT_PAUSE_THREAD:
                    pause_thread = message.pause
                # START OR STOP CHECKING DRIVER STATUS
                elif message.event == EVENT_CHECK_STATUS:
                    check_status = not check_status
                # REQUEST DRIVER STATUS UPDATE
                elif message.event == EVENT_DRIVER_UPDATE:
                    # id change
                    if hasattr(message, "driver_id"):
                        driver_id = message.driver_id
                        dispatch_event(event=EVENT_DRIVER_UPDATE,
                                    driver_id=driver_id)
                    # status change
                    elif hasattr(message, "status"):
                        icabbi.setstatus(
                            driver_id, host, message.status, message.reason)
                # HOST CHANGE
                elif message.event == EVENT_HOST_UPDATE:
                    host = message.host
                    dispatch_event(event=EVENT_HOST_UPDATE, host=host)
                # CHANGE JOB STATUS
                elif message.event == EVENT_BOOKING_UPDATE:
                    icabbi.update_booking(
                        driver_id, host, message.booking_id, message.status)
                    dispatch_event(event=EVENT_BOOKING_UPDATE,
                                status=message.status)
                # REQUEST BOOKING ARCHIVE
                elif message.event == EVENT_BOOKING_ARCHIVE:
                    bookings = []
                    # get start of week time stamp
                    #utc_week_start = icabbi.get_start_week_utc(datetime.datetime.now())
                    for offset in message.offsets:
                        bookings += icabbi.getbookingarchive(driver_id, host, row_offset=offset)
                    takings = sort_weekly_earnings(bookings)
                    dispatch_event(event=EVENT_BOOKING_ARCHIVE, bookings=bookings, takings=takings)
                # REQUEST TO KICK A DRIVER
                elif message.event == EVENT_KICK_DRIVERS:
                    latitude, longitude = Globals.gps.getgps()
                    driver = icabbi.getstatus(driver_id, host, latitude, longitude)
                    if int(driver["status"]) == 1:
                        _kick_drivers(driver, host, dispatch_event)
                # REQUEST MESSAGE ARCHIVE
                elif message.event == EVENT_MESSAGE_ARCHIVE:
                    messages = icabbi.getmessagearchive(driver_id, host)
                    dispatch_event(event=EVENT_MESSAGE_ARCHIVE, messages=messages)
                # REQUEST EXTENDED MESSAGE
                elif message.event == EVENT_MESSAGE:
                    message = icabbi.getmessage(driver_id, host, message.id)
                    dispatch_event(event=EVENT_MESSAGE, message=message)
                # SEND MESSAGE TO DISPATCH
                elif message.event == EVENT_MESSAGE_DISPATCH:
                    reply = icabbi.notify_dispatch(driver_id, host, message.text)
                    dispatch_event(event=EVENT_MESSAGE_DISPATCH, message=reply)
                # INITIATE THE GPS LISTENER
                elif message.event == EVENT_ANDROID_START_GPS:
                    if not SCGps.is_listening:
                        Globals.gps.start_gps_listener()
                # ENABLE OR DISABLE AUTOMATIC BIDDING
                elif message.event == EVENT_CHANGE_BIDDING:
                    settings["auto_bidding"] = message.enable
                    globals.save_settings(settings)
                    dispatch_event(event=EVENT_CHANGE_BIDDING, enable=settings["auto_bidding"])
            except queue.Empty:
                pass

            if pause_thread == False:
                if check_status:
                    # CHECK STATUS EVERY n SECONDS
                    if not Globals.zoneids:
                        # global zoneids not loaded then retrieve them from the server
                        Globals.zoneids = icabbi.getzoneids(driver_id, host)
                    try:
                        # SET DRIVER GPS AND RETRIEVE DRIVER STATUS
                        latitude, longitude = Globals.gps.getgps()
                        if latitude != 0.0 and longitude != 0.0:
                            driver = icabbi.getstatus(driver_id, host, latitude, longitude)
                            # CHECK JOB OFFER
                            joboffer = _check_job_offers(driver, host)
                            if joboffer:
                                dispatch_event(event=EVENT_JOB_OFFER,
                                            accepted=True, offer=joboffer)
                                # reset the state values and start next loop
                                previous_state = _new_default_states()
                            else:
                                # No Job offer
                                status = int(driver.get("status", 3))
                                # Has Driver Status changed since previous loop?
                                if previous_state["status"] != status:
                                    if status == 1:
                                        # DRIVER IS WAITING FOR JOB
                                        # Check Jobs on Bidding system
                                        if settings["auto_bidding"]:
                                            bids = icabbi.getbids(driver_id, host)
                                        else:
                                            bids = []
                                        if bids:
                                            shortest_distance_bid = smart_bidding(bids, (latitude, longitude), settings)
                                            if shortest_distance_bid:
                                                icabbi.place_bid(driver_id, host, shortest_distance_bid["id"])
                                                dispatch_event(event=EVENT_BID_UPDATE, bid=shortest_distance_bid)
                                            # reset the state to default in case bid is successful
                                            previous_state = _new_default_states()
                                        else:
                                            # No Jobs availible
                                            # Check Zone information
                                            _zone, _zones = _has_zone_changed(driver, host, previous_state["zone"])
                                            # Filter Zones with Jobs only
                                            is_sort_zones = globals.Globals.settings.get("zone_jobs_only", True)
                                            # Get Pre-Booking jobs and add to Zones
                                            _zones = sort_prebookings(driver_id, host, _zones)
                                            # check for zones with jobs
                                            sorted_zones = icabbi.sortzones(_zones, jobs=is_sort_zones)
                                            # Notify Main Thread of Zones
                                            dispatch_event(event=EVENT_ZONES, zones=sorted_zones)
                                            # Check for Driver Zone changes
                                            if _zone:
                                                if "ext_zone_info" in _zone:
                                                    # Get extended Zone information
                                                    _drivers_to_process = _zone["ext_zone_info"]["drivers"]
                                                    # eliminate Driver from list of Drivers within same Zone
                                                    drivers = list(filter(lambda d: d["id"] != driver["id"], _drivers_to_process))
                                                else:
                                                    drivers = []
                                                dispatch_event(event=EVENT_ZONE_UPDATE, driver=driver, zone=_zone, drivers=drivers)
                                                previous_state["zone"] = _zone
                                    elif status == 2:
                                        # DRIVER IS ON JOB
                                        if "bookings" in driver:
                                            booking_info = icabbi.getbooking(
                                                driver_id, host, driver["bookings"][0]["id"])
                                            # save state of status and reset zone state
                                            previous_state["status"] = status
                                            previous_state["zone"] = _new_default_zone()
                                            dispatch_event(
                                                event=EVENT_NEW_JOB, driver=driver, booking=booking_info)
                                    else:
                                        # LOGGED OUT OR ON BREAK
                                        previous_state["status"] = status
                                        previous_state["zone"] = _new_default_zone()
                                        dispatch_event(event=EVENT_LOGGED_OUT)
                    except icabbi.NetworkExceptions as err:
                        previous_state = _new_default_states()
                        dispatch_event(event=EVENT_NETWORK_ERROR, message=str(err))
                else:
                    previous_state = _new_default_states()
            print(f"Latitude: {latitude}\nLongitude: {longitude}")
        return True
    except Exception as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_str = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        dispatch_event(event=EVENT_THREAD_EXCEPTION, error=error_str)
        return False


def send_message(**kwargs):
    """ adds and event to global thread queue """
    Globals.queue.put_nowait(_kwargs2tuple("QueueMessage", **kwargs))


def _kwargs2tuple(tuple_name, **kwargs):
    """ converts named argument parameters to namedtuple also adds a time stamp """
    kwargs['TIME_STAMP'] = time.time()
    
    return namedtuple(tuple_name, list(kwargs.keys()))(*list(kwargs.values()))


def _dispatch_event(callback, **kwargs):
    """ sends a namedtuple to a callback function. If using Kivy make sure @mainthread decorator is used """
    return callback(_kwargs2tuple("Reply", **kwargs))
