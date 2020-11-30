# -*- coding=utf-8 -*-
#!/usr/bin/env python


__author__ = "Paul Millar"
__version__ = "1.0.1"

import json
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import socket
import time
import csv
import math
from io import StringIO
import datetime
from collections import namedtuple


UK6 = "http://uk6.coolnagour.com"
UK7 = "http://uk7.coolnagour.com"


NetworkExceptions = (urllib.error.HTTPError, urllib.error.URLError, OSError, socket.timeout, socket.error)

verbose_mode = True

def http_request(url="", data={}, request_type="GET"):
    if request_type == "POST":
        encoded_data = urllib.parse.urlencode(data)
        utf8 = encoded_data.encode("utf-8")
    else:
        utf8 = None
    request = urllib.request.Request(url, utf8)    
    request.add_header("User-Agent", "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-J105H Build/LMY47V)")
    response = urllib.request.urlopen(request)
    bytes_ = response.read()
    utf8chars = bytes_.decode("utf-8")
    global verbose_mode
    if verbose_mode:
        print(f"\n\n=========== {request_type} Request ===========")
        print(f"URL: {url}")
        print(f"Data: {repr(data)}")
        print(f"Response: {utf8chars}")
        print("======================================================")
    return utf8chars


def _strip_dict(_dict, key):
    """ returns the sub dictionary from the response """
    try:
        stripped = _dict["response"][key]
    except KeyError:
        stripped = {}
    finally:
        return stripped


def getstatus(driver_id, host_addr, latitude=None, longitude=None):
    """
    setgps(driver_id, host_addr, latitude(float), longitude(float)) --> dict

    sends the drivers latitude and longitude gps. Returns a Driver dict. If Latitude and Longitude
    not given then basic GET request will be sent will still return the same dict
    status of the given driver id. status: 1 = availible, 2 = on job, 3 = logged out

    returns: Multiple json strings depending on driver status
    Status = 1.
        Key      Type              Value
        -------  ----------------  --------------------------------------------------------------------------------------------------------
        status   <type 'int'>      1
        updated  <type 'int'>      -1
        zones    <type 'list'>     [{u'status': u'INSIDE', u'position': u'1', u'total': u'1', u'zone_id': u'15735', u'title': u'BLUEBELL'}]
        t        <type 'int'>      1543238972770
        panic    <type 'unicode'>  1
        id       <type 'int'>      13233

    status 2:
        Key       Type           Value
        --------  -------------  ---------------------------------------------------------------------------------------------------------------------
        status    <type 'int'>   2
        bookings  <type 'list'>  [{u'status': u'ENROUTE', u'request_place': u'1', u'site_id': u'108', u'id': u'31016699', u'request_id': u'30289673'}]
        updated   <type 'int'>   -1
        id        <type 'int'>   13241
        t         <type 'int'>   1543396113819

    status 3:
        Key     Type                  Value
        ------  ------------  -------------
        status  <type 'int'>              3
        reason  <type 'int'>              3
        id      <type 'int'>          20020
        t       <type 'int'>  1543396423267

    Status can also contain offers list these are the properties availible in an offer dict.

    offers[0]:
        Key               Type              Value
        ----------------  ----------------  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        priority          <type 'str'>      4
        prompt            <type 'int'>      1
        zone_id           <type 'unicode'>  16851
        distance          <type 'float'>    313.00411192
        pickup_date       <type 'int'>      1543505027
        workflow          <type 'dict'>     {'type': 'JOB'}
        line3             <type 'str'>      <i>0.17 MI </i>
        line2             <type 'str'>      <b><font style="color:orange">NILBOG</font><b><br
        line1             <type 'str'>      NEW JOB
        hide destination  <type 'str'>      1
        booking_id        <type 'int'>      348102
        driver_id         <type 'str'>      12323
        timeout           <type 'str'>      20
        type              <type 'str'>      JOB
        id                <type 'int'>      991479
        booking           <type 'dict'>     {'id': '18427435'}
        description       <type 'str'>      {"p":"UNIVERSITY, CONGREGATION HALL , NORWICH, NORWICH, NR47TJ","i":"","ui":"IVR CUSTOMER","f":"","n":"IVR CUSTOMER: ","m":"00447718177254","d":"AS ADVISED","t":1,"nt":"","e":0,"o":"UNIVERSITY, CONGREGATION HALL , NORWICH, NORWICH, NR47TJ","a":"","nm":"IVR CUSTOMER: ","ca":"0","pd":"","pz":"UNIVERSITY","dz":"","v":"R4","cs":3}

    """
    if latitude != None and longitude != None:
        # set gps coordinates
        latnlng = "{lat:f},{lng:f}".format(lat=latitude, lng=longitude)
        parameters = urllib.parse.urlencode(
            {"a": "d", "l": latnlng, "i": driver_id, "ga": "3", "ge": "1"})
    else:
        # don't set gps
        parameters = urllib.parse.urlencode({"a": "d", "i": driver_id})
    response = http_request("{host}/rest/drivers/{drvid}?{param}".format(host=host_addr, drvid=driver_id, param=parameters))
    return _strip_dict(json.loads(response), "driver")


def setstatus(driver_id, host_addr, driver_status, driver_reason):
    """
    setstatus(driver_id, host_addr, driver_status, driver_reason) --> dict

    Sets the status of the given driver id. status: 1 = login, 2 = ?, 3 = logout
    """
    response = http_request(url="{host}/rest/drivers/{driverid}".format(host=host_addr, driverid=driver_id),
                            data={"status": driver_status, "reason": driver_reason},
                            request_type="POST")
    return _strip_dict(json.loads(response), "driver")


def getbookingarchive(driver_id, host_addr, traverse="desc", order="pickup_date", limit_amount="100", row_offset="0"):
    """
    getbookingarchive(driverid, host_addr, traverse="desc", order="pickup_date", limit_amount="100", row_offset="0") --> list of booking dicts

    Retrieves drivers last 100 bookings. row_offset can be incrmented by 100 everytime to traverse through the next 100 bookings

    Properties:

        Key                  Type              Value
        -------------------  ----------------  -------------------------------------------------------------------------------------------------------------------------------------------------------
        booked_date          <type 'int'>      1543348208
        site                 <type 'dict'>     {u'title': u'ABC Taxis '}
        driver_id            <type 'int'>      13226
        close_date           <type 'int'>      1543348949
        lng                  <type 'float'>    1.241876
        id                   <type 'int'>      30872489
        perma_id             <type 'unicode'>  30277825A
        fee                  <type 'int'>      0
        destination          <type 'unicode'>  RYDAL CLOSE, NORWICH, NR5 8LT
        priority             <type 'int'>      4
        source               <type 'unicode'>  APP
        vehicle              <type 'dict'>     {u'plate': 4457, u'ref': u'P6'}
        driver_instructions  <type 'unicode'>  Account Ref: VISA DEBIT-APP
                                               Account Name: VISA DEBIT
        finish_status        <type 'unicode'>  COMPLETED
        user_name            <type 'unicode'>  MEGAN RIGGEY
        status               <type 'unicode'>  COMPLETED
        account_type         <type 'unicode'>  CARD
        destination_lat      <type 'float'>    52.63254
        discount             <type 'int'>      0
        user                 <type 'dict'>     {u'phone': 447710794656, u'id': 1645494, u'name': u'MEGAN RIGGEY'}
        address              <type 'unicode'>  UNIVERSITY, LCR, NORWICH, NR4 7TJ
        lat                  <type 'float'>    52.621841
        data                 <type 'unicode'>  ""
        payment              <type 'dict'>     {u'status': u'PROCESSED', u'fee': 0, u'total': 6, u'authcode': u'AuthCode: 749367', u'extras': 0, u'tip': 0, u'id': 31161159, u'meter': 6, u'tolls': 0}
        account              <type 'dict'>     {u'ref': u'VISA DEBIT-APP', u'id': 19113, u'name': u'VISA DEBIT'}
        zone_id              <type 'int'>      13714
        pickup_date          <type 'int'>      1543348800
        booking_id           <type 'int'>      31005824
        created_date         <type 'int'>      1543343839
        contact_date         <type 'int'>      1543348714
        destination_lng      <type 'float'>    1.237783
    """
    url = ("{host}/rest/drivers/{drvid}/bookingarchives?"
           "a=d&i={drvid}&bookingarchives.order={_order_};{_traverse_}&"
           "bookingarchives.limit={_limit_},{_offset_}&extended=1").format(
        host=host_addr, drvid=driver_id, _order_=order, _traverse_=traverse,
        _limit_=limit_amount, _offset_=row_offset)
    response = http_request(url)
    return _strip_dict(json.loads(response), "bookingarchives")


def set_booking_payment(driver_id, host, bookingid, charged_miles, mileage):
    data = urllib.parse.urlencode({"status": "PAYMENT", "charged_mileage": charged_miles, "mileage": mileage})
    url = "{}/rest/drivers/{}/bookings/{}?gb=0.0&ge=1&i={}".format(host, driver_id, bookingid, driver_id)
    return url, data


def set_booking_event(driverid, host, price, mileage, cost, charged_mileage):
    data = urllib.parse.urlencode({"data": '{"action":"meter:pause","price":"{}","cost":"{}","mileage":"0","charged_mileage":"0.0"}'.format(price, cost)})
    data = urllib.parse.quote(data)
    url = "{}/rest/drivers/{}/event?gb=0.0&ge=1&mpf={}&mpw=0.0&ga=9.0&i={}&gl=55.0&gs=0.0&mpl=0.0&mpt=0.0&mpe=0.0".format(host, driverid, price, driverid)
    return url, data


def set_booking_transaction(driverid, host, bookingid, price):
    url = "{}/rest/booking/{}/transaction?gb=0.0&ge=1&mpf={}&i={}".format(host, bookingid, price, driverid)
    return url


def join_zone(driverid, host, zoneid):
    data = urllib.parse.urlencode({"ids": zoneid})
    url = "{}/rest/zones/join?a=d&i={}".format(host, driverid)
    return url, data


def cancel_booking(driverid, host, bookingid, comment):
    """
    cancel_booking(driverid, host, bookingid, message) --> reply

    Sends a void request to dispatch

    Properties:
    comment <type 'str'> extra information for dispatch
    """
    response = http_request(url="{}/rest/drivers/{}/bookings/{}?a=d&i={}".format(host, driverid, bookingid, driverid),
    data={"status":"noshow", "comment": comment, "call_log": "[]"})
    return response


def getbooking(driver_id, host_addr, booking_id):
    """
    getbooking(driverid, host_addr, bookingid) --> booking dict

    Returns booking information of the specified driver and booking id

    properties:
        Key                    Type              Value
        ---------------------  ----------------  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        pin                    <type 'int'>      174458956
        booked_date            <type 'int'>      1543393868
        notice                 <type 'unicode'>  This booking has multiple pickups and dropoffs, please see extra info
        prebooked              <type 'int'>      1
        lng                    <type 'float'>    1.293681
        id                     <type 'int'>      31015648
        stc_distance           <type 'int'>      800
        perma_id               <type 'unicode'>  30280968A
        pickup_order           <type 'int'>      2
        priority               <type 'int'>      3
        source                 <type 'unicode'>  DISPATCH
        pickup_date            <type 'int'>      1543394700
        active_segment         <type 'dict'>     {u'status': u'DROPPINGOFF', u'type': u'PICKUP', u'id': 45012042}
        status                 <type 'unicode'>  DROPPINGOFF
        updated                <type 'int'>      1543394958
        pickup_date_formatted  <type 'unicode'>  08:45 (PB)
        account_type           <type 'unicode'>  CASH
        offer                  <type 'int'>      0
        route_type             <type 'unicode'>  REGULAR
        site_id                <type 'int'>      108
        created_date           <type 'int'>      1543352048
        user                   <type 'dict'>     {u'phone': u'00447879446199', u'email': u'godknows@gmail.com', u'name': u'REMAINING PASSENGERS', u'direct_connect': u'01603672984', u'id': 1757267}
        lat                    <type 'float'>    52.625781
        payment_prepaid        <type 'bool'>     False
        request_place          <type 'int'>      1
        vehicle_type           <type 'unicode'>  4 Seater
        data                   <type 'dict'>     {u'approved_address': 1, u'address_id': 29876219, u'zone': {u'id': 13708}, u'destination': u'FINISH AT NORWICH RAILWAY STATION, NORWICH, NR11EF Zone: TRAIN STATION', u'area_id': 18821, u'destination_lat': 52.626926, u'reason': 4, u'destination_id': 18412839, u'destination_type': u'ADDRESS', u'driver_instructions': u'PICKUP JOSHI AT 3 FULFORD CLOSE , NORWICH, NR46AL (Phone: 01603672984Note: 09.30)<br/><br/>PICKUP JOSHI AT ST. STEPHENS STREET, NORWICH, NR13QL (Phone: 01603672984)<br/><br/>FINAL DESTINATION: NORWICH RAILWAY STATION, NORWICH, NR11EF<br/><br/>4 Seater<br/>', u'user_name': u'REMAINING PASSENGERS', u'destination_lng': 1.306493}
        payment                <type 'dict'>     {u'status': u'NEW', u'profile': u'NORMAL', u'fee': 0, u'tariff_id': 2820, u'tariff': {u'mileagebands': [{u'extra_commission': 0, u'minimum_price': 3.8, u'price_rate_per_time': 0, u'commission_rate_per_metre': 0, u'extra_price': 0, u'distance_to': 1609, u'cost_rate_per_time': 0, u'minimum_cost': 3.8, u'cost_rate_per_metre': 0, u'price_rate_per_metre': 0, u'extra_cost': 0, u'max_price': 0}, {u'distance_from': 1609, u'extra_commission': 0, u'minimum_price': 0.5, u'price_rate_per_time': 0, u'commission_rate_per_metre': 0, u'extra_price': 0, u'distance_to': 8047, u'cost_rate_per_time': 0, u'minimum_cost': 0.5, u'cost_rate_per_metre': 0.00086992, u'price_rate_per_metre': 0.00086992, u'extra_cost': 0, u'max_price': 0}, {u'distance_from': 8047, u'extra_commission': 0, u'minimum_price': 0.5, u'price_rate_per_time': 0, u'commission_rate_per_metre': 0, u'extra_price': 0, u'distance_to': 12070, u'cost_rate_per_time': 0, u'minimum_cost': 0.5, u'cost_rate_per_metre': 0.00086992, u'price_rate_per_metre': 0.00086992, u'extra_cost': 0, u'max_price': 0}, {u'distance_from': 12070, u'extra_commission': 0, u'minimum_price': 0.5, u'price_rate_per_time': 0, u'commission_rate_per_metre': 0, u'extra_price': 0, u'distance_to': 24945, u'cost_rate_per_time': 0, u'minimum_cost': 0.5, u'cost_rate_per_metre': 0.00086992, u'price_rate_per_metre': 0.00086992, u'extra_cost': 0, u'max_price': 0}, {u'distance_from': 24945, u'extra_commission': 0, u'minimum_price': 0.5, u'price_rate_per_time': 0, u'commission_rate_per_metre': 0, u'extra_price': 0, u'distance_to': 40234, u'cost_rate_per_time': 0, u'minimum_cost': 0.5, u'cost_rate_per_metre': 0.00086992, u'price_rate_per_metre': 0.00086992, u'extra_cost': 0, u'max_price': 0}, {u'distance_from': 40234, u'extra_commission': 0, u'minimum_price': 0.5, u'price_rate_per_time': 0, u'commission_rate_per_metre': 0, u'extra_price': 0, u'distance_to': 56327, u'cost_rate_per_time': 0, u'minimum_cost': 0.5, u'cost_rate_per_metre': 0.00086992, u'price_rate_per_metre': 0.00086992, u'extra_cost': 0, u'max_price': 0}, {u'distance_from': 56327, u'extra_commission': 0, u'minimum_price': 1, u'price_rate_per_time': 0, u'commission_rate_per_metre': 0, u'extra_price': 0, u'distance_to': 80467, u'cost_rate_per_time': 0, u'minimum_cost': 1, u'cost_rate_per_metre': 0.00086992, u'price_rate_per_metre': 0.00086992, u'extra_cost': 0, u'max_price': 0}, {u'distance_from': 80467, u'extra_commission': 0, u'minimum_price': 1, u'price_rate_per_time': 0, u'commission_rate_per_metre': 0, u'extra_price': 0, u'distance_to': 16487729, u'cost_rate_per_time': 0, u'minimum_cost': 1, u'cost_rate_per_metre': 0.00086992, u'price_rate_per_metre': 0.00086992, u'extra_cost': 0, u'max_price': 0}], u'time_rounding': 60, u'rounding': 0.5, u'type': u'DISTANCE', u'mileage_rounding': 0, u'min_cost': 6, u'min_extra': 0, u'via_price': 0.5, u'min_price': 6, u'cost_rate_per_time': 0, u'price_rate_per_time': 0, u'via_cost': 0.5, u'max_extra': 0, u'increment_extra': 0, u'ref': u'DEFAULT R4', u'min_commission': 0, u'rounding_cost': 1}, u'tip_type': u'ABSOLUTE', u'tip': 0, u'discount_price': 0, u'tolls': 0, u'extras': 0, u'discount_price_type': u'PERCENTAGE', u'discount_cost': 0, u'total': 0, u'discount_cost_type': u'PERCENTAGE', u'id': 31164320}
        payment_id             <type 'int'>      31164320
        distance               <type 'int'>      5000
        payment_process        <type 'bool'>     True
        config                 <type 'dict'>     {u'satnav_uri': u'geo:52.626926,1.306493', u'satnav_query': u'52.626926,1.306493', u'satnav_source': 1, u'capture_fare': True, u'change_destination': 1, u'display_type': 0}
        arrive_date            <type 'int'>      1543394774
        payment_type           <type 'unicode'>  CASH
        request_id             <type 'int'>      30280968
        dispatch_type          <type 'unicode'>  NORMAL
        contact_date           <type 'int'>      1543394883

    """
    response = http_request("{host}/rest/drivers/{drvid}/bookings/{bkid}?a=d&i={drvid}&extended=3".format(
        host=host_addr, drvid=driver_id, bkid=booking_id))
    return _strip_dict(json.loads(response), "booking")


def getprebookings(driver_id, host_addr):
    """
    getprebookings(driver_id, host_addr) --> list of booking dicts

    properties:

        Key                Type              Value
        -----------------  ----------------  -----------------------------------------------------------------
        relative_position  <type 'float'>    1086.65648695
        data               <type 'dict'>     {u'driver_instructions': u'11.57 TRAIN', u'address_id': 18422319}
        id                 <type 'int'>      30224639
        perma_id           <type 'int'>      30224639
        user_id            <type 'int'>      1513820
        zone_id            <type 'int'>      13691
        zone               <type 'dict'>     {u'ref': u'ROU', u'id': 13691, u'title': u'ROUEN'}
        attributegroup     <type 'unicode'>  ANY
        priority           <type 'int'>      2
        release            <type 'int'>      11
        pickup_date        <type 'int'>      1543230900

    """
    response = http_request("""{host}/rest/drivers/{drvid}/requests/hour?a=d&i={drvid}""".format(
        host=host_addr, drvid=driver_id))
    return _strip_dict(json.loads(response), "requests")


def update_booking(driver_id, host_addr, booking_id, status):
    """
    update_booking(driver_id, host_addr, booking_id, status) --> dict

    updates the current booking by passing in status.
    status:
    arrived     - sends a notification to the customer and sets driver status to ARRIVED
    madecontact - sends a pickup notification to dispatch and sets the driver status to DROPPINGOFF

    returns:
    message - {"title": string, "body": string}
    response - {"booking": booking_dict}
    """
    response = http_request(url="{host}/rest/drivers/{drvid}/bookings/{bkid}?a=d&i={drvid}".format(host=host_addr, bkid=booking_id, drvid=driver_id),
                            data={"status": status, "contact_date": str(int(time.time())), "call_log": "[]"},
                            request_type="POST")
    return json.loads(response)


def getbids(driver_id, host_addr):
    """
    getbids(driver_id, host_addr) --> list of dictionaries

    Parses and returns jobs on the icabbi bidding server. Call place_bid(driver_id, zoneid) with zoneid being one of the ids
    contained within the returned dictionaries.

    dict:

        Key    Type            Value
        -----  --------------  ---------
        lat    <type 'float'>  52.34324
        lng    <type 'float'>  1.2828982
        bids   <type 'int'>    2
        id     <type 'str'>    12133
        title  <type 'str'>    FOO
    """
    response = http_request("{host}/rest/zones/bids?a=d&i={drvid}".format(host=host_addr, drvid=driver_id))
    if "{}" not in response:
        return json.loads(response)["response"]["zones"]
    else:
        return []


def place_bid(driver_id, host_addr, zone_id):
    """
    place_bid(driver_id, host_addr, zoneid) --> string

    Bid on an availible job. zoneid will be the id of the zone to which the job recides in.
    call getbids(driver_id) first to get a list of availible jobs
    """
    response = http_request(url="{host}/rest/drivers/{driverid}/offers?a=d&i={driverid}".format(host=host_addr, driverid=driver_id),
                            data={"response": "ACCEPTED", "zone_id": str(zone_id)},
                            request_type="POST")
    return response


def reply2joboffer(driver_id, host_addr, booking_id, reply):
    """
    reply2joboffer(driver_id, host_addr, booking_id, **kwargs) --> string

    accept job: reply = ACCEPTED
    decline job: reply = DECLINED
    """
    query = {"response": reply.upper()}
    if reply.upper() == "ACCEPTED":
        query["stc"] = "1"
    url = "{host}/rest/drivers/{driverid}/offers/{bkid}?a=d&i={driverid}".format(
        host=host_addr, driverid=driver_id, bkid=booking_id)
    response = http_request(url=url, data=query, request_type="POST")
    return response


def getzoneids(driver_id, host_addr):
    """
    getzoneids(driverid, host_addr) --> list of tuples

    Retrieves all known zone names and their ids
    """
    response = http_request("{host}/rest/zones?a=d&i={drvid}&zones.order=title;asc".format(host=host_addr, drvid=driver_id))
    return json.loads(response)["response"]["zones"]


def getzone(driver_id, host_addr, zone_id):
    """
    getzone(driver_id, , host_addr, zoneid) --> zone dict on success or error dict on error

    Parses and returns a dict either containing Plot information and Driver list
    or Error if unsuccessful. Driver information maybe limited depending on the
    type of package the carrier has purchased.

    If successful then function will return a dictionary containing two keys: info(dict), drivers(list of dicts)

    If Error then dictionary will contain text dump of the tables which failed to parse: 

        Key           Type           Value
        ------------  -------------  --------
        tables        <type 'list'>  [['{}']]
        table-length  <type 'int'>   1
    """
    resp = http_request("{host}/rest/zones/{znid}?a=d&i={drvid}&extended=3".format(host=host_addr, znid=zone_id, drvid=driver_id))
    zone = json.loads(resp)["response"]["zone"]
    return zone


def getzones(driver_id, host_addr):
    """
    getzones(driver_id, host_addr) --> list of zone dicts

    Returns a list containing dicts of zone information
    Zone properties:

        Key                Type          Value   Description
        -----------------  ------------  ------- -----------
        job_count          <type 'int'>  0       jobs availible
        current_driver_id  <type 'int'>  0       driver id
        total              <type 'int'>  0       total drivers
        stats              <type 'str'>  ~3      job in zone
        id                 <type 'int'>  0       zone id

    """
    response = http_request("{host}/rest/zones?a=d&i={drvid}&extended=2&zones.order=activity;desctitle;asc".format(host=host_addr, drvid=driver_id))
    lst = json.loads(response)["response"]["zones"]
    new_zones = []
    for zone in lst:
        new_zone = {"id": str(zone["id"])}
        if "total" in zone:
            new_zone["total"] = str(zone["total"])
        else:
            new_zone["total"] = "0"
        if "stats" in zone:
            new_zone["stats"] = "~3"
            new_zone["job_count"] = str(zone["stats"]["request_count"])
        else:
            new_zone["job_count"] = "0"
            new_zone["stats"] = ""
        new_zones.append(new_zone)
    return new_zones


def sortzones(zones, **kwargs):
    """ 
    sortzones(zones, **kwargs) --> [sorted_zones]
    zones  -- list of zones usually retrieved from getzones
    kwargs:
        jobs     -     bool    -    sort zones by jobs
        drivers  -     bool    -    sort zones by drivers on zone
    example - sortzones(zones, jobs=True, drivers=True) will retrieve both drivers and jobs on same plot
    """
    jobs = kwargs.get("jobs")
    drivers = kwargs.get("drivers")
    if jobs and drivers:
        return [zone for zone in zones if int(zone["job_count"]) > 0]
    elif jobs and not drivers:
        return [zone for zone in zones if int(zone["job_count"]) > 0]
    elif drivers and not jobs:
        return [zone for zone in zones if zone["job_count"] == '0']
    else:
        return zones


def getmessagearchive(driver_id, host_addr):
    """
    getmessagearchive(driver_id, host_addr) --> list of message dict

    returns the drivers message history
    Message:

        Key       Type              Value
        --------  ----------------  --------------------
        dateread  <type 'int'>      1543470247
        created   <type 'int'>      1543470243
        read      <type 'int'>      1
        id        <type 'int'>      18771945
        message   <type 'unicode'>  Your booking has bee
        type      <type 'unicode'>  SERVER
        response  <type 'int'>      1
    """
    response = http_request("{host}/rest/drivers/{drvid}/messages?messages.order=created;desc&extended=1".format(host=host_addr, drvid=driver_id))
    return _strip_dict(json.loads(response), "messages")


def getmessage(driver_id, host_addr, message_id):
    """
    getmessage(driverid, host_addr, messageid) --> dict

    returns the full message with more information
    Message:

        Key        Type              Value
        ---------  ----------------  ---------------------------------------------------------------
        dateread   <type 'int'>      1543470247
        created    <type 'int'>      1543470243
        read       <type 'int'>      1
        response   <type 'int'>      1
        driver_id  <type 'int'>      13233
        client_id  <type 'int'>      664
        message    <type 'unicode'>  Your booking has been updated. The following changes were made:

                                    Pickup 1: Destination updated.

                                    Please check extra information for any further changes.

                                    29/11/2018 05:44
        type       <type 'unicode'>  SERVER
        id         <type 'int'>      18771945
    """
    response = http_request("{host}/rest/drivers/{drvid}/messages/{msgid}?i={drvid}&extended=1".format(host=host_addr, drvid=driver_id, msgid=message_id))
    return _strip_dict(json.loads(response), "message")


def notify_dispatch(driver_id, host_addr, message):
    """ sends a message to dispatch returns {} if successful """
    response = http_request(url="{host}/rest/drivers/{drvid}/basemessages?a=d&i={drvid}".format(host=host_addr, drvid=driver_id), 
                            data={"message": message}, 
                            request_type="POST")
    return response


def findzonebyid(zones, _id):
    try:
        z = list(filter(lambda zone: zone["id"] == int(_id), zones))[0]
    except IndexError:
        z = None
    finally:
        return z


# Misc functions that arent particuary related to the driver api
def getdistance(origin, destination):
    """calculate between two gps positions in miles"""
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 3959  # miles

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d


def milestometres(miles):
    """converts miles to metres"""
    return int(float(miles) * 1609.344)


def metrestomiles(metres):
    """converts metres to miles"""
    return int(float(metres) / 1609.344)
    

def convert_time_to_readable(epoch_time):
    """ convert_time_to_readable(epoch_time) -> FormattedTime(day, hour, min) """
    s = time.localtime(float(epoch_time))
    day = time.strftime("%A ", s)
    hour = time.strftime("%H", s)
    _min = time.strftime("%M", s)
    return namedtuple("FormattedTime", ["day", "hour", "min"])(day, hour, _min)


def get_start_week_utc(dt):
    """
    get_start_week_utc(dt) --> float

    Parameters:
        dt:                 datetime tuple. If not sure just pass in datetime.datetime.now() (current time)
    Returns:
        unix_time_stamp     float unix time stamp. of the beginning of the week from dt
    """
    # get the beginning of the week from datetime tuple
    monday_dt = dt - datetime.timedelta(days=dt.weekday())
    # reset to 0 minutes
    string_to_format = "{}/{}/{}/00/00/00".format(monday_dt.day, monday_dt.month, monday_dt.year)
    unix_time_tuple = time.strptime(string_to_format, "%d/%m/%Y/%H/%M/%S")
    unix_time_stamp = time.mktime(unix_time_tuple)
    return unix_time_stamp

# dictionary containing key lists of hosts and valid driver ids
# seven represents host 7 and holds as of typing this a handful of Goldstar taxi
# Ids. host 6 holds ABC drivers. there are many more which I haven't documented
# there proberbly is a better way of finding a specific driver but
# not all taxi firms have the same icabbi features
host_ids = {
    'seven': 
            ['20002', '20020', '20026', '20037', '20042', '20045', '20058', 
            '20078', '20086', '20128', '20176', '20177', '20178', '20180', 
            '20188', '20217', '20225', '20231', '20250', '20259', '20269', 
            '20280', '20297', '20302', '20355', '20359', '20369', '20388', 
            '20404', '18992', '19108', '19648', '19649', '19650', '19651', 
            '19652', '19653', '19654', '19655', '19656', '19657', '19665', 
            '19681', '19705', '19706', '19707', '19254', '19255', '19256', 
            '19284', '19285', '19286', '19287', '19288', '19289', '19290', 
            '19291', '19292', '19293', '19294', '19295', '19296', '19297', 
            '19298', '19299', '19300', '19301', '19302', '19303', '19304', 
            '19305', '19306', '19308', '19310', '19311', '19312', '19313', 
            '19314', '19315', '19316', '19317', '19319', '19320', '19964', 
            '19974'], 
    'six': 
            ['19152', '13222', '13227', '13230', '13228', '13224', '13225', '13233', '13226', 
            '13234', '13223', '13229', '13232', '13238', '13231', '13239', '13235', 
            '13236', '13237', '13248', '13243', '13245', '13250', '13241', '13240', 
            '13251', '13246', '13257', '13258', '13244', '13242', '13254', '13259', 
            '13249', '13253', '13256', '13247', '13268', '13260', '13266', '13267', 
            '13271', '13270', '13263', '13272', '13262', '13269', '13277', '13275', 
            '13264', '13278', '13274', '13273', '13261', '13265', '13279', '13281', 
            '13284', '13285', '13289', '13288', '13283', '13287', '13280', '13286', 
            '13292', '13294', '13282', '13293', '13295', '13296', '13299', '13298', 
            '13297', '13291', '13290', '13303', '13301', '13302', '13309', '13304', 
            '13308', '13307', '13300', '13306', '13305', '13310', '13314', '13311', 
            '13315', '13316', '13319', '13313', '13318', '13312', '13317', '13324', 
            '13327', '13326', '13328', '13323', '13322', '13329', '13325', '13321', 
            '13330', '13334', '13331', '13335', '13333', '13338', '13339', '13336', 
            '13332', '13337', '13344', '13341', '13349', '13347', '13345', '13346', 
            '13348', '13350', '13340', '13343', '13351', '13342', '13352', '13353', 
            '13356', '13354', '13355', '13357', '13359', '13358', '13368', '13365', 
            '13360', '13366', '13364', '13361', '13362', '13363', '13369', '13367', 
            '13370', '13372', '13371', '13840', '14262', '14263', '15098', '15097', 
            '15096', '15102', '15101', '15103', '15107', '15158', '15173', '15444', 
            '15447', '15463', '15494', '15530', '15549', '15540', '15551', '15582', 
            '15615', '15668', '15682', '15690', '15719', '15747', '15771', '15770', 
            '15773', '15781', '15780', '15789', '15822', '15823', '15831', '15866', 
            '15864', '15865', '15872', '15909', '15912', '15932', '15937', '15938', 
            '15954', '15960', '16501', '16522', '16538', '16537', '16591', '16641', 
            '16659', '16660', '16662', '16690', '16692', '16695', '16706', '16739', 
            '16741', '16758', '16789', '16788', '16790', '16793', '16802', '16945', 
            '16958', '16962', '16988', '16989', '16990', '17013', '17039', '17070', 
            '17133', '17141', '17156', '17154', '17161', '17179', '17198', '17194', 
            '17218', '17217', '17220', '17248', '17252', '17291', '17294', '17299', 
            '17304', '17332', '17331', '17338', '17333', '17347', '15438', '16722', 
            '16751', '16970', '17062', '17134', '17193', '17297', '17367', '17366']}


def _main():
    global verbose_mode
    verbose_mode = False
    DRIVERID = "13223"
    print("Retrieving Zone IDs...")
    zone_ids = getzoneids(DRIVERID, UK6)
    zone_total = 0
    driver_total = 0
    drivers_on_job = 0
    drivers_no_job = 0
    print("Scanning Zones for drivers")
    for zoneid in zone_ids:
        zone_total += 1
        zone = getzone(DRIVERID, UK6, zoneid["id"])
        if "drivers" in zone:
            for driver in zone["drivers"]:
                driver_total += 1
                if driver["status"] == 1:
                    drivers_no_job += 1
                elif driver["status"] == 2:
                    drivers_on_job += 1
    print(f"{zone_total} Zones searched...")
    print(f"Total drivers: {driver_total}")
    print(f"Drivers on Job: {drivers_on_job}")
    print(f"Drivers not working: {drivers_no_job}")

if __name__ == '__main__':
    _main()
