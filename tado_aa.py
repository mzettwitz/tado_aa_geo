#
# tado_aa.py (Tado Auto-Assist for Geofencing and Open Window Detection)
# Created by Adrian Slabu <adrianslabu@icloud.com> on 11.02.2021
# Edited by Martin Zettwitz on 05.04.2025
#

import sys
import time
import os

from datetime import datetime
from PyTado.interface import Tado

def main():

    global lastMessage
    global use_geo_fencing
    global checkingInterval
    global errorRetringInterval
    global enableLog
    global logFile
    global TOKEN_FILE

    TOKEN_FILE = "/tado_token/token"

    lastMessage = ""

    #Settings
    #--------------------------------------------------
    use_geo_fencing = os.getenv("GEOFENCING", 'False').lower() in ('true', '1')

    checkingInterval = 10.0 # checking interval (in seconds)
    errorRetringInterval = 30.0 # retrying interval (in seconds), in case of an error

    enableLog = False # activate the log with "True" or disable it with "False"
    logFile = "/l.log" # log file location
    #--------------------------------------------------

    if (use_geo_fencing is True):
        print("Geo Fencing enabled.")
    else:
        print("Geo Fencing disabled.")

    login()
    homeStatus()
    
def login():

    global t

    try:
        t = Tado(token_file_path=TOKEN_FILE)
        status = t.device_activation_status()
         
        TOKEN_FILE_EXISTS = os.path.isfile(TOKEN_FILE)
 
        if status == "PENDING":
            url = t.device_verification_url()
            print(f"Please visit this URL to authenticate:\n")
            print(f'{url}')
            t.device_activation()
            status = t.device_activation_status()
 
        if status == "COMPLETED":
            if TOKEN_FILE_EXISTS:
                print("Login successful.")
            else:
                print("Login successful. Refresh token saved.")
        else:
            print(f"Login failed. Current status: {status}\nRetrying")
            time.sleep(errorRetringInterval)
            login()
        
    except KeyboardInterrupt:
        printm ("Interrupted by user.")
        sys.exit(0)

    except Exception as e:
        if (str(e).find("Permission denied") != -1):
            printm (str(e))
            login()
        else:
            printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
            time.sleep(errorRetringInterval)
            login()    

def homeStatus():
    
    global devicesHome

    try:
        homeState = t.get_home_state()["presence"]
        devicesHome = []
        if (use_geo_fencing is False):
            devicesHome.append("no_fencing")

        for mobileDevice in t.get_mobile_devices():
            if (mobileDevice["settings"]["geoTrackingEnabled"] == True):
                if (mobileDevice["location"] != None):
                    if (mobileDevice["location"]["atHome"] == True):
                        devicesHome.append(mobileDevice["name"])

        if (lastMessage.find("Connection Error") != -1 or lastMessage.find("Waiting for the device location") != -1):
            printm ("Successfully got the location, everything looks good now, continuing..\n")

        if (use_geo_fencing is False):
            devicesHome.clear()
        elif (len(devicesHome) > 0 and homeState == "HOME"):
            if (len(devicesHome) == 1):
                printm ("Your home is in HOME Mode, the device " + devicesHome[0] + " is at home.")
            else:
                devices = ""
                for i in range(len(devicesHome)):
                    if (i != len(devicesHome) - 1):
                        devices += devicesHome[i] + ", "
                    else:
                        devices += devicesHome[i]
                printm ("Your home is in HOME Mode, the devices " + devices + " are at home.")
        elif (len(devicesHome) == 0 and homeState == "AWAY"):
            printm ("Your home is in AWAY Mode and are no devices at home.")
        elif (len(devicesHome) == 0 and homeState == "HOME"):
            printm ("Your home is in HOME Mode but are no devices at home.")
            printm ("Activating AWAY mode.")
            t.set_away()
            printm ("Done!")
        elif (len(devicesHome) > 0 and homeState == "AWAY"):
            if (len(devicesHome) == 1):
                printm ("Your home is in AWAY Mode but the device " + devicesHome[0] + " is at home.")
            else:
                devices = ""
                for i in range(len(devicesHome)):
                    if (i != len(devicesHome) - 1):
                        devices += devicesHome[i] + ", "
                    else:
                        devices += devicesHome[i]
                printm ("Your home is in AWAY Mode but the devices " + devices + " are at home.")

            printm ("Activating HOME mode.")
            t.set_home()
            printm ("Done!")

        devicesHome.clear()
        printm ("Waiting for a change in devices location or for an open window..")
        time.sleep(1)
        engine()

    except KeyboardInterrupt:
        printm ("Interrupted by user.")
        sys.exit(0)

    except Exception as e:
        if (str(e).find("location") != -1):
            printm ("I cannot get the location of one of the devices because the Geofencing is off or the user signed out from tado app.\nWaiting for the device location, until then the Geofencing Assist is NOT active.\nWaiting for an open window..")
            time.sleep(1)
            engine()
        elif (str(e).find("NoneType") != -1):
            time.sleep(1)
            engine()
        else:
            printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
            time.sleep(errorRetringInterval)
            homeStatus()

def engine():

    while(True):
        try:
            #Open Window Detection
            for z in t.get_zones():
                    zoneID = z["id"]
                    zoneName = z["name"]
                    if (t.get_open_window_detected(zoneID)["openWindowDetected"] == True):
                        printm (zoneName + ": open window detected, activating the OpenWindow mode.")
                        t.set_open_window(zoneID)
                        printm ("Done!")
                        printm ("Waiting for a change in devices location or for an open window..")
            #Geofencing
            homeState = t.get_home_state()["presence"]

            devicesHome.clear()
            if (use_geo_fencing is False):
                devicesHome.append("no_fencing")

            for mobileDevice in t.get_mobile_devices():
                if (mobileDevice["settings"]["geoTrackingEnabled"] == True):
                    if (mobileDevice["location"] != None):
                        if (mobileDevice["location"]["atHome"] == True):
                            devicesHome.append(mobileDevice["name"])

            if (lastMessage.find("Connection Error") != -1 or lastMessage.find("Waiting for the device location") != -1):
                printm ("Successfully got the location, everything looks good now, continuing..\n")
                printm ("Waiting for a change in devices location or for an open window..")

            if (use_geo_fencing is False):
                devicesHome.clear()
            elif (len(devicesHome) > 0 and homeState == "AWAY"):
                if (len(devicesHome) == 1):
                    printm (devicesHome[0] + " is at home, activating HOME mode.")
                else:
                    devices = ""
                    for i in range(len(devicesHome)):
                        if (i != len(devicesHome) - 1):
                            devices += devicesHome[i] + ", "
                        else:
                            devices += devicesHome[i]
                    printm (devices + " are at home, activating HOME mode.")
                t.set_home()
                printm ("Done!")
                printm ("Waiting for a change in devices location or for an open window..")

            elif (len(devicesHome) == 0 and homeState == "HOME"):
                printm ("Are no devices at home, activating AWAY mode.")
                t.set_away()
                printm ("Done!")
                printm ("Waiting for a change in devices location or for an open window..")

            devicesHome.clear()
            time.sleep(checkingInterval)

        except KeyboardInterrupt:
                printm ("Interrupted by user.")
                sys.exit(0)

        except Exception as e:
                if (str(e).find("location") != -1 or str(e).find("NoneType") != -1):
                    printm ("I cannot get the location of one of the devices because the Geofencing is off or the user signed out from tado app.\nWaiting for the device location, until then the Geofencing Assist is NOT active.\nWaiting for an open window..")
                    time.sleep(checkingInterval)
                else:
                    printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
                    time.sleep(errorRetringInterval)

def printm(message):
    global lastMessage
    
    if (enableLog == True and message != lastMessage):
        try:
            with open(logFile, "a") as log:
                log.write(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " # " + message + "\n")
                log.close()

        except Exception as e:
            sys.stdout.write(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " # " + str(e) + "\n")

    if (message != lastMessage):
        lastMessage = message
        sys.stdout.write(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " # " + message + "\n")
main()
