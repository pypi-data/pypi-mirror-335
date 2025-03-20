#!/usr/bin/env python
#-------------------------------------------------------------------------------
# qwiic_scd4x_ex3_disable_auto_calibration.py
#
# This example disables automatic calibration and 
# prints the current CO2 level, relative humidity, and temperature in C.
#-------------------------------------------------------------------------------
# Written by SparkFun Electronics, December 2024
#
# This python library supports the SparkFun Electroncis Qwiic ecosystem
# 
# More information on Qwiic is at https://www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#===============================================================================
# Copyright (c) 2024 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
#===============================================================================

import qwiic_scd4x
import sys
import time

def runExample():
	print("\nQwiic SCD4x Example 3 - Disable Auto Calibration\n")

	# Create instance of device
	mySCD4x = qwiic_scd4x.QwiicSCD4x() 

	# Check if it's connected
	if mySCD4x.is_connected() == False:
		print("The device isn't connected to the system. Please check your connection", file=sys.stderr)
		return

	# Initialize the device

	# begin() has three boolean parameters:
   	# measBegin: set to true to begin periodic measurements automatically;
    #            set to false to leave periodic measurements disabled.
    #            Default is true.
   	# autoCalibrate: set to true to leave automatic calibration enabled;
    #                set to false to disable automatic calibration.
    #                Default is true.
   	# skipStopPeriodicMeasurements: set to true to make .begin skip the initial call of stopPeriodicMeasurement;
    #                               set to false to make .begin stop periodic measurements before doing anything else.
    #                               Default is false.
  	# Please see the next example for a full description of skipStopPeriodicMeasurements

	# In this example we call begin and set autoCalibrate to false to disable automatic calibration
	if mySCD4x.begin(autoCalibrate=False) == False:
		print("Error while initializing device", file=sys.stderr)
		return

	while True:
		if mySCD4x.read_measurement(): # This must be called to get new data. It will return false until new data is available 
			print("\nCO2(ppm):", mySCD4x.get_co2())
			print("Temperature(C):", mySCD4x.get_temperature())
			print("Humidity(%RH):", mySCD4x.get_humidity())
		else:
			print(".", end="")
		
		time.sleep(0.5) # Only check for new data every 0.5 second

if __name__ == '__main__':
	try:
		runExample()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Example")
		sys.exit(0)