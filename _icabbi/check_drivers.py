from . import icabbi
import json
import time
driver_ids_iter = iter(json.loads(open("GOLDSTAR_DRIVERS.json", "r").read())["drivers"])
try:
    while True:
        try:
            driverid = next(driver_ids_iter)
            driver = icabbi.getstatus(driverid, icabbi.UK7)
            if int(driver["status"]) == 1 or int(driver["status"]) == 2:
                bks = icabbi.getbookingarchive(driver["id"], icabbi.UK7)
                money = 0.0
                print("ID: ", driver["id"])
                print("Status: ", driver["status"])
                if "zones" in driver:
                    print("Title: ", driver["zones"][0]["title"])
                def isbooking_ondate(booking):
                    pickup_date = float(booking["pickup_date"])
                    unixtime = time.ctime(pickup_date)
                    tm_struct = time.strptime(unixtime)
                    return tm_struct.tm_year == 2019 and tm_struct.tm_mday == 0o4
                bks = list(filter(isbooking_ondate, bks))
                for bk in bks:
                    money += float(bk["payment"]["meter"])
                print("Driver {} has earnt GBP {} today\n\n".format(driver["id"], money))
        except ValueError as err:
            print(err)
except StopIteration:
    pass
