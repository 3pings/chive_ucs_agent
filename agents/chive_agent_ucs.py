from ucsmsdk.ucshandle import UcsHandle
import subprocess
import os
import time
import json

# Get user provided information from bash script and parse it

ucsm_ip = os.environ['UCSM_IP']
ucsm_username = os.environ['UCSM_USERNAME']
ucsm_password = os.environ['UCSM_PASSWORD']


def ucsm_login():
    try:
        print "Testing for ping response...."
        response = subprocess.check_output(
            ['ping', '-c', '3', ucsm_ip],
            stderr=subprocess.STDOUT,  # get all output
            universal_newlines=True  # return string not bytes
        )
        handle = UcsHandle(ucsm_ip, ucsm_username, ucsm_password)
        handle.login()
        return handle
    except:
            response = None
            print "Unable to ping IP address provided. Exiting...."
            exit()


def getTemps():

    equipID_list = handle.query_classid("computeRackUnit")

    # create lists - one for server DN, Model and Name
    equipDN_list = []
    equipName_list = []
    equipModel_list = []
    for equipID in equipID_list:
        equipDN_list.append(equipID.dn)
        equipName_list.append(equipID.name)
        equipModel_list.append(equipID.model)

    # get temperature stats
    #temps_list = handle.query_classid("processorEnvStats")
    temps_list = handle.query_classid("computeRackUnitMbTempStats")


    # front_temp = The current temperature (in Celsius) at the front section of the rack-mount server motherboard.
    # ioh1 = The current temperature (in Celsius) at I/O hub 1 of the rack-mount server motherboard.

    # create list - one for server DN
    tempsDN_list = []
    tempsFront_list = []
    tempsIOH_list = []
    tempsTime_list = []
    condition_list = []

    c = 0

    for temps in temps_list:
        tempsDN_list.append(temps.dn)
        tempsFront_list.append(temps.front_temp)
        tempsIOH_list.append(temps.ioh1_temp)
        tempsTime_list.append(temps.time_collected)


        # Change string to integer for temperature value
        TMP = tempsIOH_list[c]
        if TMP == 'not-applicable':
            int_temp = 0
        else:
            int_temp = int(float(TMP))


        if int_temp is 0:            # temp is "not-applicable"
            condition = "PENDING - Host powered off"
            condition_list.append(condition)
        elif int_temp >= 60:         # temp is greater than 60 degrees C
            condition = "high"
            condition_list.append(condition)
        elif int_temp >= 48:       # temp between 48 and 60 degrees C
            condition = "elevated"
            condition_list.append(condition)
        else:                      # temp less than 48 degrees C
            condition = "normal"
            condition_list.append(condition)

        # take day/time returned and place into two separate variables
        date = tempsTime_list[c].split('T')[0]  # date occurs before 'T' in  ts string
        time = tempsTime_list[c].split('T')[1]  # time occurs after 'T' in  ts string
        time = time.split('.')[0]  # remove microseconds from time occurring after period

        obj = {"dn": equipDN_list[c],
               "attributes": {"temp": tempsIOH_list[c], "timestamp": time, "date": date, "condition": condition_list[c],
                              "type": equipModel_list[c]}}
        print obj
        c = c+1


        # send object to RESTAPI function
        upload = send2_RESTAPI(obj)

        if upload:
            print "device successfully uploaded to api (L)"
        else:
            print "error uploading device "


def send2_RESTAPI(obj):
    # try to post a request - if web server is down just keep going
    try:
        while True:
            headers = {"Content-Type": "application/json"}
            rsp = requests.post('http://app:5000/device', headers=headers, data=json.dumps(obj))
            return rsp.ok
    except:
        print "API microservice not running...keep getting data..."
        pass

def ucsm_logout(handle):
    handle.logout()

if __name__ == "__main__":
    try:
        handle = ucsm_login()
        while True:
            getTemps()
            time.sleep(60)
        while False:
            print "logging out now...."
            ucsm_logout(handle)
    except KeyboardInterrupt:  # allow user to break loop
        print("Manual break by user - CTRL-C")
