#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
© Copyright 2020, Yoshiyuki Karezaki <y.karezaki@gmail.com>.
mission_import_autopilot.py: 

2020.07.04 ドローンエンジニア養成塾 Course2 実践ワークショップ課題。
指定された URL のミッションを実行するスクリプト。
DroneKit Python の mission_import_export.py を追加・修正して --url, --file オプションを追加。

--url mission_waipoints_url     指定された URL からミッションファイルをダウンロードし実行
--file mission_waipoints_file   指定されたミッションファイルを実行

準備:
$ pip2 install requests # モジュールインストール
$ sim_vehicle.py -v ArduCopter --custom-location=35.68407150,139.75523470,17,353 --map # SITL 起動

実行方法:
$ ./mission_import_autopilot.py --connect 127.0.0.1:14551
※オプションを省略すると http://winggate.co.jp/mission_9th.waypoints からミッションファイルをダウンロード

© Copyright 2015-2016, 3D Robotics.
mission_import_export.py: 

This example demonstrates how to import and export files in the Waypoint file format 
(http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format). The commands are imported
into a list, and can be modified before saving and/or uploading.

Documentation is provided at http://python.dronekit.io/examples/mission_import_export.html
"""
from __future__ import print_function


from dronekit import connect, Command, VehicleMode
import time

import requests
import sys

START_ALTITUDE = 20 # 自動飛行開始するの高さ
URL = 'http://winggate.co.jp/mission_9th.waypoints'
# sim_vehicle.py -v ArduCopter --custom-location=35.68407150,139.75523470,17,353 --map

def download():
    r = requests.get(URL)
    f = open(FILE, 'w')
    f.write(r.content)
    f.close()

#download()

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Demonstrates mission import/export from a file.')
parser.add_argument('--connect', 
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")

# Add mission waypoints options
parser.add_argument('--url',
                   help="mission waypoints url")
parser.add_argument('--file',
                   help="mission waypoints file")

args = parser.parse_args()

connection_string = args.connect
sitl = None

#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

# Check that vehicle is armable. 
# This ensures home_location is set (needed when saving WP file)

while not vehicle.is_armable:
    print(" Waiting for vehicle to initialise...")
    time.sleep(1)

def readmission(aFileName):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print("\nReading mission from file: %s" % aFileName)
    cmds = vehicle.commands
    missionlist=[]
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i==0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray=line.split('\t')
                ln_index=int(linearray[0])
                ln_currentwp=int(linearray[1])
                ln_frame=int(linearray[2])
                ln_command=int(linearray[3])
                ln_param1=float(linearray[4])
                ln_param2=float(linearray[5])
                ln_param3=float(linearray[6])
                ln_param4=float(linearray[7])
                ln_param5=float(linearray[8])
                ln_param6=float(linearray[9])
                ln_param7=float(linearray[10])
                ln_autocontinue=int(linearray[11].strip())
                cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist


def upload_mission(aFileName):
    """
    Upload a mission from a file. 
    """
    #Read mission from file
    missionlist = readmission(aFileName)
    
    print("\nUpload mission from a file: %s" % aFileName)
    #Clear existing mission from vehicle
    print(' Clear mission')
    cmds = vehicle.commands
    cmds.clear()
    #Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' Upload mission')
    vehicle.commands.upload()


def download_mission():
    """
    Downloads the current mission and returns it in a list.
    It is used in save_mission() to get the file information to save.
    """
    print(" Download mission from vehicle")
    missionlist=[]
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist

def save_mission(aFileName):
    """
    Save a mission in the Waypoint file format 
    (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
    """
    print("\nSave mission from Vehicle to file: %s" % aFileName)    
    #Download mission from vehicle
    missionlist = download_mission()
    #Add file-format information
    output='QGC WPL 110\n'
    #Add home location as 0th waypoint
    home = vehicle.home_location
    output+="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (0,1,0,16,0,0,0,0,home.lat,home.lon,home.alt,1)
    #Add commands
    for cmd in missionlist:
        commandline="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cmd.seq,cmd.current,cmd.frame,cmd.command,cmd.param1,cmd.param2,cmd.param3,cmd.param4,cmd.x,cmd.y,cmd.z,cmd.autocontinue)
        output+=commandline
    with open(aFileName, 'w') as file_:
        print(" Write mission to file")
        file_.write(output)
        
        
def printfile(aFileName):
    """
    Print a mission file to demonstrate "round trip"
    """
    print("\nMission file: %s" % aFileName)
    with open(aFileName) as f:
        for line in f:
            print(' %s' % line.strip())        


def readmission_from_url(aUrl):
    """
    Load a mission from a url into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print("\nReading mission from url: %s" % aUrl)
    cmds = vehicle.commands
    missionlist=[]
    r = requests.get(aUrl)
    lines = r.text.split('\n')
    i = 0
    for line in lines:
        if i==0:
            if not line.startswith('QGC WPL 110'):
                raise Exception('File is not supported WP version')
        else:
            linearray=line.split('\t')
            ln_index=int(linearray[0])
            ln_currentwp=int(linearray[1])
            ln_frame=int(linearray[2])
            ln_command=int(linearray[3])
            ln_param1=float(linearray[4])
            ln_param2=float(linearray[5])
            ln_param3=float(linearray[6])
            ln_param4=float(linearray[7])
            ln_param5=float(linearray[8])
            ln_param6=float(linearray[9])
            ln_param7=float(linearray[10])
            ln_autocontinue=int(linearray[11].strip())
            cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
            missionlist.append(cmd)
        i += 1
    return missionlist

def upload_mission_from_url(aUrl):
    """
    Upload a mission from a url. 
    """
    #Read mission from file
    missionlist = readmission_from_url(aUrl)
    
    print("\nUpload mission from a url: %s" % aUrl)
    #Clear existing mission from vehicle
    print(' Clear mission')
    cmds = vehicle.commands
    cmds.clear()
    #Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' Upload mission')
    vehicle.commands.upload()

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

        
    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)


import_mission_filename = 'mpmission.txt'
export_mission_filename = 'exportedmission.txt'

mission_waipoints_url = None

if args.url:
    mission_waipoints_url = args.url
elif args.file:
    import_mission_filename = args.file
else:
    mission_waipoints_url = URL

if mission_waipoints_url:
    #Upload mission from url
    upload_mission_from_url(mission_waipoints_url)
else:    
    #Upload mission from file
    upload_mission(import_mission_filename)

#Download mission we just uploaded and save to a file
#save_mission(export_mission_filename)

# Arm and Takeoff
arm_and_takeoff(START_ALTITUDE)

# Set mode to AUTO to start mission
vehicle.mode = VehicleMode("AUTO")

#Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()


#print("\nShow original and uploaded/downloaded files:")
#Print original file (for demo purposes only)
#printfile(import_mission_filename)
#Print exported file (for demo purposes only)
#printfile(export_mission_filename)
