__version__ = "0.3.1"
__author__ = "Paul Millar"

from flask import Flask
from flask import render_template
from flask import request
import json
import random
import time
from collections import namedtuple
from subprocess import PIPE, Popen
import re

random.seed(time.time())

app = Flask(__name__)

usernames = ("Paul", "Simon", "Peter", "Sharon", "Elizabeth", "Mrs Maple")
address = ("12 Newmarket Street", "Norwich City Council", "Saxon Air Amsterdam Way", "Hellesdon High School", "Goldtsar Taxi Whiffler Road",
           "67 Gertrude Road", "528 Dereham Road", "7 Maple Drive", "89 Tuckswood Lane")

Zone = namedtuple("Zone", ["id", "job_count", "driver_count", "delimeter"])


class Globals:

    # load zone json
    zones = {"13737": "BEESTON", "13736": "BROADLAND", "13735": "AIRPORT", "13734": "S.MANOR", "13733": "DUSSINDALE", "13732": "KESWICK", "13731": "CHAPEL BREAK", "13730": "BOWTHORPE", "13739": "OLD COSTESSEY", "13738": "OVAL", "13718": "TUCKSWOOD", "13689": "ST BENEDICTS", "13780": "WROXHAM", "13720": "HENBY", "13721": "HEARTSEASE", "13722": "SPROWSTON", "13688": "CATHEDRAL", "13724": "FIFERS", "13725": "HELLESDON", "13726": "ASDA", "13727": "WHITLINGHAM", "13728": "THORPE ST ANDREWS", "13729": "THREE SCORE", "13694": "THORPE HEIGHTS", "13695": "KETTS PLUMSTEAD", "13696": "SILVER", "13697": "CATTON", "13690": "CHAPELFIELD", "13691": "ROUEN", "13692": "RIVERSIDE", "13693": "TRAIN STATION", "13889": "THE WASH", "13698": "MILE CROSS", "13699": "WOODCOCK", "13761": "DEREHAM", "13755": "BLO/BRU", "13754": "HORSFORD", "13757": "BROOKE", "13756": "WYMONDHAM", "13751": "WITTON", "13750": "PORINGLAND", "13753": "SPIXWORTH", "13752": "RACKHEATH", "13759": "YARMOUTH", "13758": "NORTH WALSHAM", "15584": "DUKE", "15732": "BLUEBOAR", "15735": "BLUEBELL", "13746": "BAWBURGH", "13747": "HETHERSETT", "13744": "EASTON", "13745": "COLNEY", "13742": "DRAYTON", "13743": "TAVERHAM", "13740": "HAMPDON", "13741": "QUEENS HILL", "13748": "MULBARTON", "13749": "DUNSTON", "13877": "SUSSEX", "13779": "REEPHAM", "13778": "ACLE", "15809": "LONG STRATTON", "15808": "BECCLES", "15807": "POTTER HEIGHAM", "15806": "CROMER", "15805": "RINGLAND", "15804": "BRAMERTON", "15803": "LODDON", "15802": "SWAFFHAM", "15801": "AYLSHAM", "15800": "IPSWICH", "15797": "SURREY", "15795": "BUS STATION", "13357": "Prince Of Wales", "15799": "ATTLEBOROUGH", "15798": "HINGHAM", "13887": "BASE", "13764": "THETFORD", "13760": "FAKENHAM", "13888": "RICHMOND", "13762": "LOWESTOFT", "13763": "DISS", "15811": "INTWOOD", "15816": "SALHOUSE", "15817": "JUDGES", "13812": "STANSTED", "13810": "HEATHROW", "13811": "GATWICK", "13719": "TROWSE", "13897": "BULL", "13890": "HOTBLACK", "13711": "MARLPIT", "13710": "SWEET BRIAR", "13713": "WEST EARLHAM", "13712": "NORTH EARLHAM", "13715": "NORFOLK NORWICH HOSP", "13714": "UNIVERSITY", "13717": "EATON", "13716": "CRINGLEFORD", "13782": "SOUTH EAST", "13783": "LONDON", "15676": "THORPE END", "13781": "WATTON", "13786": "SCOTLAND", "13787": "MIDLANDS", "13784": "WALES", "13785": "SOUTH", "13788": "SOUTH WEST", "13789": "NORTH ENGLAND", "15678": "WATERFRONT", "15679": "GUILDHALL", "13708": "EATON RISE", "13709": "SOUTH PARK", "13702": "EARLHAM", "13703": "UNTHANK", "13700": "SPROWSTON ROAD", "13701": "OLD PALACE", "13706": "COLMAN", "13707": "JESSOP", "13704": "LAKENHAM", "13705": "HEWITT", "13723": "OLD CATTON"}
    # random generated zones response string
    # load zoneids string
    zone_ids_string = """{"response":{"zones":[{"id":13778,"title":"ACLE"},{"id":13735,"title":"AIRPORT"},{"id":13726,"title":"ASDA"},{"id":15799,"title":"ATTLEBOROUGH"},{"id":15801,"title":"AYLSHAM"},{"id":13887,"title":"BASE"},{"id":13746,"title":"BAWBURGH"},{"id":15808,"title":"BECCLES"},{"id":13737,"title":"BEESTON"},{"id":13755,"title":"BLO\/BRU"},{"id":15735,"title":"BLUEBELL"},{"id":15732,"title":"BLUEBOAR"},{"id":13730,"title":"BOWTHORPE"},{"id":15804,"title":"BRAMERTON"},{"id":13736,"title":"BROADLAND"},{"id":13757,"title":"BROOKE"},{"id":13897,"title":"BULL"},{"id":15795,"title":"BUS STATION"},{"id":13688,"title":"CATHEDRAL"},{"id":13697,"title":"CATTON"},{"id":13731,"title":"CHAPEL BREAK"},{"id":13690,"title":"CHAPELFIELD"},{"id":13706,"title":"COLMAN"},{"id":13745,"title":"COLNEY"},{"id":13716,"title":"CRINGLEFORD"},{"id":15806,"title":"CROMER"},{"id":13761,"title":"DEREHAM"},{"id":13763,"title":"DISS"},{"id":13742,"title":"DRAYTON"},{"id":15584,"title":"DUKE"},{"id":13749,"title":"DUNSTON"},{"id":13733,"title":"DUSSINDALE"},{"id":13702,"title":"EARLHAM"},{"id":13744,"title":"EASTON"},{"id":13717,"title":"EATON"},{"id":13708,"title":"EATON RISE"},{"id":13760,"title":"FAKENHAM"},{"id":13724,"title":"FIFERS"},{"id":13811,"title":"GATWICK"},{"id":15679,"title":"GUILDHALL"},{"id":13740,"title":"HAMPDON"},{"id":13721,"title":"HEARTSEASE"},{"id":13810,"title":"HEATHROW"},{"id":13725,"title":"HELLESDON"},{"id":13720,"title":"HENBY"},{"id":13747,"title":"HETHERSETT"},{"id":13705,"title":"HEWITT"},{"id":15798,"title":"HINGHAM"},{"id":13754,"title":"HORSFORD"},{"id":13890,"title":"HOTBLACK"},{"id":15811,"title":"INTWOOD"},{"id":15800,"title":"IPSWICH"},{"id":13707,"title":"JESSOP"},{"id":15817,"title":"JUDGES"},{"id":13732,"title":"KESWICK"},{"id":13695,"title":"KETTS PLUMSTEAD"},{"id":13704,"title":"LAKENHAM"},{"id":15803,"title":"LODDON"},{"id":13783,"title":"LONDON"},{"id":15809,"title":"LONG STRATTON"},{"id":13762,"title":"LOWESTOFT"},{"id":13711,"title":"MARLPIT"},{"id":13787,"title":"MIDLANDS"},{"id":13698,"title":"MILE CROSS"},{"id":13748,"title":"MULBARTON"},{"id":13715,"title":"NORFOLK NORWICH HOSP"},{"id":13712,"title":"NORTH EARLHAM"},{"id":13789,"title":"NORTH ENGLAND"},{"id":13758,"title":"NORTH WALSHAM"},{"id":13723,"title":"OLD CATTON"},{"id":13739,"title":"OLD COSTESSEY"},{"id":13701,"title":"OLD PALACE"},{"id":13738,"title":"OVAL"},{"id":13750,"title":"PORINGLAND"},{"id":15807,"title":"POTTER HEIGHAM"},{"id":13741,"title":"QUEENS HILL"},{"id":13752,"title":"RACKHEATH"},{"id":13779,"title":"REEPHAM"},{"id":13888,"title":"RICHMOND"},{"id":15805,"title":"RINGLAND"},{"id":13692,"title":"RIVERSIDE"},{"id":13691,"title":"ROUEN"},{"id":13734,"title":"S.MANOR"},{"id":15816,"title":"SALHOUSE"},{"id":13786,"title":"SCOTLAND"},{"id":13696,"title":"SILVER"},{"id":13785,"title":"SOUTH"},{"id":13782,"title":"SOUTH EAST"},{"id":13709,"title":"SOUTH PARK"},{"id":13788,"title":"SOUTH WEST"},{"id":13753,"title":"SPIXWORTH"},{"id":13722,"title":"SPROWSTON"},{"id":13700,"title":"SPROWSTON ROAD"},{"id":13689,"title":"ST BENEDICTS"},{"id":13812,"title":"STANSTED"},{"id":15797,"title":"SURREY"},{"id":13877,"title":"SUSSEX"},{"id":15802,"title":"SWAFFHAM"},{"id":13710,"title":"SWEET BRIAR"},{"id":13743,"title":"TAVERHAM"},{"id":13889,"title":"THE WASH"},{"id":13764,"title":"THETFORD"},{"id":15676,"title":"THORPE END"},{"id":13694,"title":"THORPE HEIGHTS"},{"id":13728,"title":"THORPE ST ANDREWS"},{"id":13729,"title":"THREE SCORE"},{"id":13693,"title":"TRAIN STATION"},{"id":13719,"title":"TROWSE"},{"id":13718,"title":"TUCKSWOOD"},{"id":13714,"title":"UNIVERSITY"},{"id":13703,"title":"UNTHANK"},{"id":13784,"title":"WALES"},{"id":15678,"title":"WATERFRONT"},{"id":13781,"title":"WATTON"},{"id":13713,"title":"WEST EARLHAM"},{"id":13727,"title":"WHITLINGHAM"},{"id":13751,"title":"WITTON"},{"id":13699,"title":"WOODCOCK"},{"id":13780,"title":"WROXHAM"},{"id":13756,"title":"WYMONDHAM"},{"id":13759,"title":"YARMOUTH"}]},"origin":"action"}
"""
    zones_response = ""
    # random bidding flag
    random_bidding = False
    # store drivers logged in
    drivers = {}
    # store random pre-bookings
    pre_bookings = {}
    # store fake messages
    fake_messages = [{'dateread': 1567552534, 'created': 1567552527, 'read': 1, 'id': 38373733, 'message': 'OK THANKS', 'type': 'INFO', 'response': 1}, {'dateread': 1567552491, 'created': 1567552491, 'read': 1, 'value': 'CAN I LOG OFF PLEASE?', 'id': 38373699, 'message': 'Driver Created', 'type': 'INFO', 'response': 1}, {'dateread': 1567552459, 'created': 1567552452, 'read': 1, 'id': 38373695, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567550223, 'created': 1567550163, 'read': 1, 'id': 38373300, 'message': 'Please note your job', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567547989, 'created': 1567547906, 'read': 1, 'id': 38373086, 'message': 'The price of this jo', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567547382, 'created': 1567547370, 'read': 1, 'id': 38372998, 'message': 'Message from previou', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567547263, 'created': 1567547248, 'read': 1, 'id': 38372993, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567545516, 'created': 1567545498, 'read': 1, 'id': 38372712, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567535874, 'created': 1567535863, 'read': 1, 'id': 38371304, 'message': 'OK', 'type': 'INFO', 'response': 1}, {'dateread': 1567535783, 'created': 1567535773, 'read': 1, 'id': 38371294, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567535694, 'created': 1567535694, 'read': 1, 'value': 'quick break after this', 'id': 38371252, 'message': 'Driver Created', 'type': 'INFO', 'response': 1}, {'dateread': 1567533772, 'created': 1567533755, 'read': 1, 'id': 38370810, 'message': 'Your bid was success', 'type': 'SERVER', 'response': 1}, {'dateread': 1567531720, 'created': 1567531686, 'read': 1, 'id': 38370424, 'message': 'JOB has been taken b', 'type': 'SERVER', 'response': 1}, {'dateread': 1567531704, 'created': 1567531686, 'read': 1, 'id': 38370423, 'message': 'Please note your job', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567530855, 'created': 1567530811, 'read': 1, 'id': 38370228, 'message': 'The price of this jo', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567530801, 'created': 1567530768, 'read': 1, 'id': 38370220, 'message': 'The price of this jo', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567525536, 'created': 1567525517, 'read': 1, 'id': 38369035, 'message': 'the queue to get out', 'type': 'INFO', 'response': 1}, {'dateread': 1567515895, 'created': 1567515848, 'read': 1, 'id': 38366016, 'message': 'Please note your job', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567515704, 'category': 'LEGAL', 'created': 1567515701, 'read': 1, 'id': 38274148, 'message': 'By continuing to use', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567465861, 'created': 1567465855, 'read': 1, 'id': 38357589, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567465620, 'created': 1567465620, 'read': 1, 'value': 'cheers', 'id': 38357571, 'message': 'Driver Created', 'type': 'INFO', 'response': 1}, {'dateread': 1567465609, 'created': 1567465597, 'read': 1, 'id': 38357570, 'message': 'YES MATE', 'type': 'INFO', 'response': 1}, {'dateread': 1567465519, 'created': 1567465519, 'read': 1, 'value': 'ok to log out after this?', 'id': 38357563, 'message': 'Driver Created', 'type': 'INFO', 'response': 1}, {'dateread': 1567464207, 'created': 1567464191, 'read': 1, 'id': 38357400, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567460651, 'created': 1567460607, 'read': 1, 'id': 38356976, 'message': 'The price of this jo', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567460125, 'created': 1567460116, 'read': 1, 'id': 38356947, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567459407, 'created': 1567459401, 'read': 1, 'id': 38356835, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567455981, 'created': 1567455974, 'read': 1, 'id': 38356250, 'message': 'The price of this jo', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567454490, 'created': 1567454488, 'read': 1, 'id': 38355871, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567453575, 'created': 1567453547, 'read': 1, 'id': 38355647, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567450706, 'created': 1567450694, 'read': 1, 'id': 38355205, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567449490, 'created': 1567449475, 'read': 1, 'id': 38354996, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567437235, 'created': 1567437220, 'read': 1, 'id': 38352074, 'message': 'OAKLAND MARINE', 'type': 'INFO', 'response': 1}, {'dateread': 1567437179, 'created': 1567437179, 'read': 1, 'value': 'did they say anywhere specific to pick them up from?', 'id': 38352061, 'message': 'Driver Created', 'type': 'INFO', 'response': 1}, {'dateread': 1567433650, 'created': 1567433646, 'read': 1, 'id': 38351143, 'message': 'Success! The custome', 'type': 'NOTICE', 'response': 1}, {'dateread': 1567433423, 'created': 1567433386, 'read': 1, 'id': 38351021, 'message': 'Comunity speed watch', 'type': 'INFO', 'response': 1}, {'dateread': 1567432720, 'created': 1567432664, 'read': 1, 'id': 38350634, 'message': 'YEP', 'type': 'INFO', 'response': 1}, {'dateread': 1567432639, 'created': 1567432639, 'read': 1, 'value': 'isnthis the community hub?', 'id': 38350623, 'message': 'Driver Created', 'type': 'INFO', 'response': 1}]


"""
{"response":{"zones":[{"id":15735,"title":"BLUEBELL","lat":52.62411032,"lng":1.24972013,"bids":1},{"id":13697,"title":"CATTON","lat":52.64639161,"lng":1.29452694,"bids":2},{"id":13877,"title":"SUSSEX","lat":52.64087847,"lng":1.28811569,"bids":1},{"id":13693,"title":"TRAIN STATION","lat":52.62530732,"lng":1.30921095,"bids":1},{"id":13713,"title":"WEST EARLHAM","lat":52.63225774,"lng":1.23694907,"bids":1}]},"origin":"action"} 
"""


def _random_bids(zoneids):
    zones = []
    random_ids = []
    for x in range(random.randint(1, 10)):
        while 1:
            random_zone = zoneids[random.randint(0, len(zoneids)-1)]
            if random_zone["id"] not in random_ids:
                random_ids.append(random_zone["id"])
                zone = {"id": random_zone["id"],
                        "title": random_zone["title"],
                        "lat": float(random.uniform(50.00000, 53.00000)),
                        "lng": float(random.uniform(0.20000, 3.00000)),
                        "bids": random.randint(1, 4)}
                zones.append(zone)
                break
    return json.dumps({"response": {"zones": zones}, "origin": "action"})


def _set_driver_status(driver, status, reason):
    """
    _set_driver_status(driver, status, reason) -> None

    Description:
        Sets the driver status and resets zones and random bidding based on the drivers status.

    Parameters:
        driver          - dict
        status          - int
        reason          - int

        driver: Dictionary object containing information about the driver
    """
    # Set the new status and reason to the Driver dict
    driver["status"] = status
    driver['reason'] = reason
    # remove booking or zone from driver dict because a new status is being updated
    if "bookings" in driver:
        driver.pop("bookings")
    if "zone" in driver:
        driver.pop("zone")
    if status == "1":
        # Driver has replotted generate a new zone and add it to the driver dict
        Globals.random_bidding = False
        print("Random bids set to false")
        # Load the Zones from Json file and generate new Zone information for each one
        #zoneids = Globals.zones
        #max_index = len(list(zoneids.keys())) - 1
        #key = list(zoneids.keys())[random.randint(0, max_index)]
        #driver['zones'] = [{"title": zoneids[key], "id": key, "zone_id": key, "position": str(random.randint(1,4))}]
        zone_ids = json.loads(Globals.zone_ids_string)["response"]["zones"]
        driver["zones"] = generate_driver_zone(zone_ids)
        driver["zone_response"] = generate_random_zones(driver["zones"][0], zone_ids)
    elif status == "2":
        # Driver is on a job. Generate a random Booking and add it to the Driver dict.
        booking = get_random_booking(str(driver["id"]))
        driver["bookings"] = [{"id": booking["id"], "status": "ENROUTE", "booking": booking}]


'''{"response":{"zones":[{"total":2,"id":13782},{"id":13750,"stats":{"request_count":1}},{"id":13718,"stats":{"request_count":1}},{"total":1,"id":13717},{"total":1,"id":13716},{"total":1,"id":13897},{"total":1,"id":13697},{"total":1,"id":13706},{"total":1,"id":15584},{"id":13702,"stats":{"request_count":2}},{"total":1,"id":13744},{"id":15679,"stats":{"request_count":1}},{"total":1,"id":13721},{"total":1,"id":13725,"stats":{"request_count":2}},{"total":1,"id":13720},{"total":1,"id":13695},{"id":13711,"stats":{"request_count":1}},{"id":13698,"stats":{"request_count":1}},{"total":1,"id":13715},{"total":1,"id":13712,"stats":{"request_count":1}},{"total":1,"id":13723},{"id":13701,"stats":{"request_count":1}},{"id":13738,"stats":{"request_count":2}},{"id":13752,"stats":{"request_count":1}},{"id":13692,"stats":{"request_count":1}},{"id":13696,"stats":{"request_count":2}},{"id":13709,"stats":{"request_count":1}},{"id":13722,"stats":{"request_count":1}},{"total":1,"id":15797},{"total":2,"id":13877},{"total":2,"id":13694,"stats":{"request_count":1}},{"total":1,"id":13693,"stats":{"request_count":3}},{"total":2,"id":13703,"stats":{"request_count":1}},{"total":1,"id":13713,"stats":{"request_count":1}}]},"origin":"action"}'''


def generate_driver_zone(zoneids):
    maxindex = len(zoneids) - 1
    driver_index = random.randint(0, maxindex)
    random_zone = zoneids[driver_index]
    driver_zone = {"id": random_zone["id"], "zone_id": random_zone["id"], "title": random_zone["title"]}
    driver_zone["position"] = random.randint(1, 4)
    return [driver_zone]


def generate_random_zone(zoneid):
    zone = {"id": zoneid["id"], "zone_id": zoneid["id"], "title": zoneid["title"]}
    zone["total"] = random.randint(0, 5)
    if random.randint(1, 3) == 2:
        zone["stats"] = {}
        zone["stats"]["request_count"] = random.randint(1, 4)
    return zone


def generate_random_zones(driver_zoneid, zoneids):
    zones = []
    zones.append(generate_random_zone(driver_zoneid))
    for zoneid in zoneids:
        if random.randint(1, 5) == 3 and int(zoneid["id"]) != int(driver_zoneid["id"]):
            zones.append(generate_random_zone(zoneid))
    return json.dumps({"response": {"zones": zones}, "origin": "action"})


def _new_job_offer(driver_id):
    """
    _new_job_offer(driver_id) -> dict

    Description:
        Generate a random Job offer and return it as a Json object
    
    Parameters:
        driver_id           - int
    """
    _min, _max = (1000, 999999)
    return {
        "id": random.randint(_min, _max), 
        "driver_id": driver_id, 
        "booking_id": random.randint(_min, _max), 
        "hide destination": "1",
        "priority": "4", 
        "type": "JOB", 
        "pickup_date": int(time.time() + 1000.0),
	    "distance": random.uniform(100.0, 600.0), 
        "zone_id": list(Globals.zones.keys())[random.randint(0, len(list(Globals.zones.keys())) - 1)], 
        "prompt": 1, 
        "timeout": "20", 
        "workflow": {"type": "JOB"},
	    "booking": {"id": "18427435"}, 
        "line1": "NEW JOB", 
        "line2": '<b><font style="color:orange">NILBOG</font><b><br',
	    "line3": " <i>0.17 MI </i>",
        "description": '{"p":"UNIVERSITY, CONGREGATION HALL , NORWICH, NORWICH, NR47TJ","i":"","ui":"IVR CUSTOMER","f":"","n":"IVR CUSTOMER: ","m":"00447718177254","d":"AS ADVISED","t":1,"nt":"","e":0,"o":"UNIVERSITY, CONGREGATION HALL , NORWICH, NORWICH, NR47TJ","a":"","nm":"IVR CUSTOMER: ","ca":"0","pd":"","pz":"UNIVERSITY","dz":"","v":"R4","cs":3}'
    }


def get_random_booking(driver_id):    
    return {
        "data": {"address": address[random.randrange(len(address)-1)], "destination": address[random.randrange(len(address) - 1)],
                 "driver_instructions": "This is a test.", "zone": {"id": "38938"}, "destination_lat": 52.624920, "destination_lng": 1.314530},
        "user": {"name": usernames[random.randrange(len(usernames) - 1)], "phone": "01603700700", "direct_connect": "01603672984", "id": "666"},
        "payment": {"id": str(random.randint(1, 9999)), "meter": str(random.randint(5, 100)), "account_meter": str(random.randint(5, 100))},
        "config": {"satnav_query": "69+Gay+Street"},
        "pickup_date": time.time(),
        "id": str(random.randint(100, 99999)),
        "status": "ENROUTE",
        "lat": 51.384620,
        "lng": -2.363490}


def _generate_prebooking(driver_id, zone_id):
    """
    _generate_prebooking(driver_id, zone_id) -> dict

    Description:
        Generate a random Pre Booking
    Parameters:
        driver_id           - int
        zone_id             - int
    """
    _idrange = (1000, 999999)
    return {"perma_id": random.randint(*_idrange),
            "user_id": random.randint(*_idrange),
            "zone_id": zone_id,
            "zone": {
        "ref": "RND",
        "id": zone_id,
        "title": zones.get(zone_id)
    },
        "relative_position": random.uniform(1000.0, 99999.9),
        "priority": random.randint(1, 5),
        "release": random.randint(1, 9),
        "taxis": 1,
        "attributegroup": "ANY",
        "pickup_date": str(int(time.time())),
        "id": driver_id
    }


def _generate_prebookings(driver_id, zones, max_range):
    """
    _generate_prebookings(driver_id, zones, max_range) -> dict

    Description:
        Generate a list of Pre-Bookings and return them as a json dict
    
    Parameters:
        driver_id           - int
        zones               - list
        max_range           - int maximum amount of zones to create
    """
    pre_bookings = [_generate_prebooking(
        driver_id, zone_id) for zone_id in _generate_zone_ids(zones, max_range)]
    return {"response": {"requests": pre_bookings, "origin": "action"}}


def _zone_info_generator(zone_id):
    """ generates random numbers for job count and driver count for that zone id and returns a namedtuple """
    if random.randrange(0, 13) > 5:
        driver_count = random.randint(1, 7)
    else:
        driver_count = 0
    if random.randrange(0, 11) > 5:
        # we got a job
        deli = "~3"
    else:
        # no job
        deli = ""
    if deli == "~3":
        # if job get how many
        job_count = random.randint(1, 5)
    else:
        # no jobs
        job_count = 0
    return Zone(zone_id, job_count, driver_count, deli)


def _generate_zone_ids(zones, zone_max_range):
    """ returns a list of random zone ids within a max range """
    zone_ids = list(zones.keys())
    if zone_max_range > len(zone_ids):
        raise IndexError("""zone_max_range is greater than zone_ids size. please use a smaller number.\n\nThe size of the zone_ids array is {_ids} zone_max_range was {max}""".format(
            _ids=len(zone_ids), max=zone_max_range))
    return list(set([zone_ids[random.randint(0, len(zone_ids))-1] for zone_id in range(zone_max_range)]))


@app.route("/get-drivers", methods=["GET"])
def get_drivers():
    return json.dumps(Globals.drivers)


@app.route("/rest/drivers/<int:driver_id>/basemessages", methods=["POST"])
def notify_base(driver_id):
    message = request.form.get("message")
    print("Driver {} has sent this message: {}".format(driver_id, message))
    return "{}"


@app.route("/rest/drivers/<int:driver_id>/messages", methods=["GET"])
def get_messages(driver_id):
    json_string = json.dumps({"response": {"messages": Globals.fake_messages}, "origin": "myarse"})
    return json_string


@app.route("/rest/drivers/<int:driverid>/messages/<int:messageid>", methods=["GET"])
def get_message(driverid, messageid):
    try:
        message = next(filter(lambda msg: msg["id"] == messageid, Globals.fake_messages))
        message["message"] = "This is the longest message in the world lol. What the hell am I talking about er? hopefullly kivy can wrap this text otherwise it will be going oveer the windows"
        json_object = {"response": {"message": message}, "origin": "myarse"}
    except IndexError:
        print("could not find ID matching {}".format(messageid))
        json_object = {}
    finally: 
        return json.dumps(json_object)


@app.route("/create-driver/<int:driver_id>", methods=["GET"])
def create_driver(driver_id):
    Globals.drivers[driver_id] = {"status": "3", "reason": "3", "id": driver_id}
    return json.dumps(Globals.drivers[driver_id])


@app.route("/delete-driver/<int:driver_id>", methods=["GET"])
def remove_driver(driver_id):
    try:
        Globals.drivers.pop(driver_id)
    except KeyError:
        return "<H1>No driver with #{_id} found</H1>".format(_id=driver_id)
    finally:
        return "<H1>OK</H1>"


def _random_booking_for_archive(driver_id):
    booking = {}
    booking["id"] = random.randint(1, 999999)
    booking["driver_id"] = driver_id
    booking["booking_id"] = booking["id"]
    booking["lat"] = 52.648856
    booking["lng"] = 1.262741
    booking["account_type"] = ("CARD", "CASH")[random.randint(0,1)]
    booking["discount"] = 0
    booking["fee"] = 0
    booking["created_date"] = int(time.time())
    booking["pickup_date"] = int(time.time())
    booking["booked_date"] = int(time.time())
    booking["contact_date"] = int(time.time())
    booking["close_date"] = int(time.time())
    booking["user_name"] = "WAYNE KING"
    booking["zone_id"] = 13710
    booking["address"] = "AMAZON LOGISTICS SWEET BRIAR ROOAD INDUSTRIAL ESTATE"
    booking["destination"] = "SENTINEL HOUSE, SURREY STREET"
    booking["destination_lat"] = 52.623574
    booking["destination_lng"] = 1.29546
    booking["driver_instructions"] = "No instructions set"
    booking["status"] = "COMPLETED"
    booking["finish_status"] = "COMPLETED"
    booking["priority"] = 3
    booking["source"] = "APP"
    booking["data"] = "\"\""
    payment = {}
    payment["id"] = random.randint(1000, 999999)
    payment["meter"] = random.randint(5, 100)
    payment["extras"] = 0
    payment["tip"] = 0
    payment["tolls"] = 0
    payment["fee"] = 0
    payment["total"] = payment["meter"]
    payment["status"] = "PROCESSED"
    payment["AuthCode"] = random.randint(1000, 200000)
    # add payment to booking
    booking["payment"] = payment
    account = {}
    account["id"] = random.randint(1000, 200000)
    account["ref"] = "VISA DEBIT-APP"
    account["name"] = "VISA DEBIT"
    # add account to booking
    booking["account"] = account
    user = {}
    user["id"] = random.randint(1000, 2000000)
    user["name"] = "WAYNE KING"
    user["phone"] = "0800911911"
    # add user to booking
    booking["user"] = user
    booking["site"] = {"title": "ABC Taxis "}
    booking["vehicle"] = {"plate": 999, "ref": "P456"}
    booking["perma_id"] = "83493489A"
    return booking


@app.route("/rest/drivers/<int:driver_id>/bookingarchives", methods=["GET"])
def get_booking_archives(driver_id):
    archives = []
    response = {"response": {"bookingarchives": archives}}
    for _ in range(100):
        archives.append(_random_booking_for_archive(driver_id))
    return json.dumps(response)


@app.route("/debug/<int:driver_id>", methods=["POST"])
def debug(driver_id):
    """
    debug(driverid) -> str

    description: change the drivers status and enviroment
    http://host:port/debug/driverid/
    Post request parameters:

    give-message:               mimicks a message sent from dispatch
    random-zones:               changes the zone information
    random-bids:                toggles the bidding randomizer to on and off
    shutdown:                   shutdown the server
    enviroment:                 returns server information
    pre-bookings:               toggles pre-bookings on and off
    job-offer:                  sends a job offer to the driver
    """
    driver = Globals.drivers.get(driver_id)
    # no post request given
    if driver == None:
        return "{drvid} not found, please create first.".format(drvid=driver_id)
    type_ = request.form.get("type")
    if type_ == "give-message":
        return "<H1>OK</H1>"
    # change zones
    elif type_ == "random-zones":
        driver["zone_response"] = generate_random_zones(json.loads(Globals.zone_ids_string["response"]["zones"]))
        return "<H1>OK</H1>"
    # enable or disable random bidding
    elif type_ == "random-bids":
        if request.form.get("enable") == "1":
            Globals.random_bidding = True
            return "random bidding has been enabled"
        else:
            Globals.random_bidding = False
            return "random bidding has been disabled"
    # shut the server down
    elif type_ == "shutdown":
        func = request.environ.get('werkzeug.server.shutdown')
        func()
        return "Shutting down"
    # get the server details
    elif type_ == "enviroment":
        info = request.environ
        return json.dumps({
            "name": info.get("SERVER_NAME"),
            "software": info.get("SERVER_SOFTWARE"),
            "remote_address": info.get("REMOTE_ADDR"),
            "request-method": info.get("REQUEST_METHOD")
        })
    # enable disable pre bookings
    elif type_ == "pre-bookings":
        if request.form.get("enable") == "1":
            Globals.pre_bookings = _generate_prebookings(
                driver_id, Globals.zones, random.randint(5, 15))
        else:
            Globals.pre_bookings = {}
        return """<H1>{enable}</H1>""".format(enable=request.form.get("enable"))
    # offer a job to the driver
    elif type_ == "job-offer":
        driver["offers"] = [_new_job_offer(driver_id)]
        return display_message("offer has been added to status json")


@app.route("/rest/zones", methods=["GET"])
def rest_zones():
    driver_id = int(request.args.get("i"))
    driver = Globals.drivers.get(driver_id, None)
    if "extended" in request.args:
        if driver:
            return driver["zone_response"]
        else:
            print("Driver not found in rest_zones(). Returning empty string may raise error on client.")
    else:
        if driver:
            return Globals.zone_ids_string
    return ""


@app.route("/rest/zones/<int:zone_id>", methods=["GET"])
def rest_ext_zone(zone_id):
    return """{"response":{"zone":{"total":4,"id":15797,"title":"SURREY","ref":"SUR","wait":10,"split_site_parking":1,"drivers":[{"id":18666,"ref":225,"position":1,"total":4,"name":"Hussain","latitude":52.628072,"longitude":1.295232,"status":1,"reason":1,"vehicle":{"seats":4,"saloon":1,"condition":3},"attributes":[{"id":1,"alias":"R4","name":"Any Vehicle"},{"id":290,"alias":"H2","name":"Eco 4 Seater"},{"id":366,"alias":"X1","name":"Exective saloon"},{"id":15,"alias":"S","name":"Saloon"}]},{"id":18536,"ref":117,"position":2,"total":4,"name":"Liviu","latitude":52.628002,"longitude":1.294998,"status":1,"reason":1,"vehicle":{"seats":4,"saloon":1,"condition":3},"attributes":[{"id":1,"alias":"R4","name":"Any Vehicle"},{"id":290,"alias":"H2","name":"Eco 4 Seater"},{"id":366,"alias":"X1","name":"Exective saloon"},{"id":15,"alias":"S","name":"Saloon"}]},{"id":17412,"ref":152,"position":3,"total":4,"name":"Reza","latitude":52.627992,"longitude":1.295215,"status":1,"reason":1,"vehicle":{"seats":4,"saloon":1,"condition":3},"attributes":[{"id":1,"alias":"R4","name":"Any Vehicle"},{"id":290,"alias":"H2","name":"Eco 4 Seater"},{"id":366,"alias":"X1","name":"Exective saloon"},{"id":15,"alias":"S","name":"Saloon"}]},{"id":13264,"ref":44,"position":4,"total":4,"name":"Ali","latitude":52.626895,"longitude":1.294448,"status":1,"reason":1,"vehicle":{"seats":4,"saloon":1,"condition":3},"attributes":[{"id":1,"alias":"R4","name":"Any Vehicle"},{"id":290,"alias":"H2","name":"Eco 4 Seater"},{"id":366,"alias":"X1","name":"Exective saloon"},{"id":15,"alias":"S","name":"Saloon"}]},{"id":13226,"ref":6,"name":"Ilhan","latitude":52.629277,"longitude":1.302067,"status":2,"reason":4,"vehicle":{"seats":4,"saloon":1,"condition":3},"booking_status":"ENROUTE","attributes":[{"id":1,"alias":"R4","name":"Any Vehicle"},{"id":290,"alias":"H2","name":"Eco 4 Seater"},{"id":8,"alias":"E","name":"Estate"},{"id":366,"alias":"X1","name":"Exective saloon"},{"id":15,"alias":"S","name":"Saloon"}]}],"stats":{"request_count":1,"active_booking_count":3,"total_drivers":5,"seats4":5}}},"origin":"action"}"""
        

@app.route("/rest/zones/bids", methods=["GET"])
def zones_bids():
    if Globals.random_bidding:
        return _random_bids(json.loads(Globals.zone_ids_string)["response"]["zones"])
    else:
        return "{}"

@app.route("/rest/drivers/<int:driver_id>/offers/<int:booking_id>", methods=["POST"])
@app.route("/rest/drivers/<int:driver_id>/offers", methods=["POST"])
def job_offer(driver_id=0, booking_id=0):
    driver = Globals.drivers.get(driver_id)
    resp = str(request.form.get("response"))
    if resp == "ACCEPTED":
        # remove offers key
        try:
            driver.pop("offers")
        except KeyError:
            pass
        # set driver id
        driver["id"] = str(driver_id)
        # set driver status to 2 and get new booking
        _set_driver_status(driver, "2", "1")
    return "{}"


@app.route("/rest/drivers/<int:driver_id>/bookings/<int:booking_id>")
def bookings(driver_id, booking_id):
    if driver_id not in Globals.drivers:
        return display_message("No driver ID created!!")
    return json.dumps({"response": {"booking": Globals.drivers.get(driver_id)["bookings"][0]["booking"]}})


@app.route("/rest/drivers/<int:driver_id>/requests/hour", methods=["GET"])
def prebookings(driver_id):
    try:
        prebookings = Globals.drivers.get(driver_id).prebookings
    except AttributeError:
        prebookings = {}
    finally:
        return json.dumps(prebookings)


@app.route("/rest/drivers/<int:driver_id>/bookings/<int:booking_id>", methods=["POST"])
def update_booking(driver_id, booking_id):
    driver = Globals.drivers.get(driver_id)
    status = request.form.get("status")
    if status == "arrived":
        driver['bookings'][0]["status"] = "ARRIVED"
    elif status == "madecontact":
        driver['bookings'][0]["status"] = "DROPPINGOFF"
    return json.dumps({"response": {"driver": driver}})


@app.route("/rest/drivers/<int:driver_id>", methods=["GET", "POST"])
def rest_drivers(driver_id):
    driver = Globals.drivers.get(driver_id)
    if driver == None:
        return display_message("No driver found with ID #{_id}. Please create driver first.".format(_id=driver_id))
    if request.method == "GET":
        return json.dumps({"response": {"driver": driver}})
    elif request.method == "POST":
        driver["id"] = str(driver_id)
        _set_driver_status(driver, request.form.get(
            "status"), request.form.get("reason"))
        return json.dumps({"response":{"driver": driver}})
    else:
        return display_message("ERROR: no GET or POST request could be found!!")


@app.route("/save/", methods=["POST"])
def save():
    data = request.form.get("data")
    filename = request.form.get("filename")
    with open(filename, "w") as fp:
        fp.write(data)
    return f"saved to {filename}"


def display_message(message):
    return render_template("index.html", output=message)


def run_server(ip_addr, port, is_debug):
    if not ip_addr:
        ip_addr = "0.0.0.0"
    if not port:
        port = 5000
    app.run(host=ip_addr, debug=is_debug, port=port)


def run_control(driverid, ip_addr, port):
    """Client control function"""
    import icabbi
    import urllib.request, urllib.error, urllib.parse
    def display_main_menu(driver_id, hostaddr):
        print("-----------------------------------------------------------")
        print("Test Server Control\nCoded by Paul Millar 2019\nVersion 0.1")
        print("Operating on Host {}. Using Driver #{}".format(hostaddr, driver_id))
        print("-----------------------------------------------------------")
        print("1 - Toggle Random bids")
        print("2 - Offer Job")
        print("3 - Change Status")
        print("4 - Replot")
        print("5 - Toggle Pre-Booking Randomizer")
        print("R - Remove driver")
        print("B - Get booking information")
        print("S - Get Driver Status")
        print("C - Shutdown down Server")
        print("I - Get Server Enviroment information")
        print("A - Accept Job")
        print("Q - Quit")
    

    def _server_request(_debug_addr, _data):
        _encoded_data = urllib.parse.urlencode(_data).encode("utf-8")
        _request = urllib.request.Request(_debug_addr, _encoded_data)
        return urllib.request.urlopen(_request).read().decode("utf-8")


    if not driverid:
        raise ValueError("No driverid specified. Please run -i or --id with driverid int value")
    if not ip_addr:
        ip_addr = "127.0.0.1"
    if not port:
        port = 5000
    host_addr = "http://{}:{}".format(ip_addr, port)
    debug_addr = "{}/debug/{}".format(host_addr, driverid)
    random_bid_enable = True
    print("Creating driver...")
    _request = urllib.request.Request("{}/create-driver/{}".format(host_addr, driverid))
    print(urllib.request.urlopen(_request).read().decode("utf-8"))
    display_main_menu(driverid, host_addr)
    while True:
        reply = input(": ")
        if reply == "q":
            print("Removing driver and exiting...")
            _request = urllib.request.Request("{}/delete-driver/{}".format(host_addr, driverid))
            print(urllib.request.urlopen(_request).read().decode("utf-8"))
            break
        elif reply == "1":
            print(_server_request(debug_addr, {
                "type": "random-bids",
                "enable": str(int(random_bid_enable))
            }))
            random_bid_enable = not random_bid_enable
        elif reply == "2":
            print(_server_request(debug_addr, {
                "type": "job-offer"
            }))
        elif reply == "4":
            print(icabbi.setstatus(driverid, host_addr, "1", "3"))
        elif reply == 's':
            drivers = json.loads(urllib.request.urlopen(host_addr + "/get-drivers").read().decode("utf-8"))
            driver = drivers[driverid]
            for key, value in list(driver.items()):
                print("{}: {}".format(key, value))
        elif reply == 'm':
            display_main_menu(driverid, host_addr)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("iCabbi Test Server")
    parser.add_argument("-r", "--run", required=True, choices=["server", "client"], dest="run", type=str, help="[server]|[client]")
    parser.add_argument("-a", "--ip", dest="ip_addr", help="define the IP address for the test server", type=str)
    parser.add_argument("-p", "--port", dest="port", help="define port address for the test server.", type=int)
    server_group = parser.add_argument_group("server")
    server_group.add_argument("-d", "--debug", action="store_true", dest="is_debug", help="Set Test server to debug mode this will prevent any other debugging tools like pdb if enabled.")
    client_group = parser.add_argument_group("client")
    client_group.add_argument("-i", "--id", dest="driverid", type=str, help="Specify the driver id you wish to use.")
    args = parser.parse_args()
    if args.run == "server":
        if not args.ip_addr:
            pipe = Popen(["ifconfig", "wlp1s0"], stdout=PIPE)
            stdout = pipe.communicate()
            stdout_string = stdout[0].decode("utf-8")
            match = re.search(r'inet ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', stdout_string)
            ip_address = match.groups(0)[0]
            port = 5000
        else:
            ip_address = args.ip_addr
            port = args.port     
        run_server(ip_address, port, True)
    else:
        pass
        #run_control(args.driverid, args.ip_addr, args.port)
