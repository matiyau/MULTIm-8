import os

#Get Path Of This Script
selfPath = os.path.dirname(os.path.abspath( __file__ ))

mst_bldDir = "/tmp/MULTIm-8_Uno"
slv_bldDir = "/tmp/MULTIm-8_ATtiny85"

#Create Required Folders Exist In /tmp Directory
for direc in [mst_bldDir, slv_bldDir] :
    os.system("rm -rf " + direc)
    os.makedirs(direc)

#Search For Arduino Install Directory In Home Folder
homeDir = os.path.expanduser('~')

ardInst = ''
for direc in os.listdir(homeDir) :
    if os.path.isdir(os.path.join(homeDir, direc)) :
        if "arduino-1." in direc :
            ardInst = os.path.join(homeDir, direc)
            break

ardInstDefault = ''
if not ardInst == '' :
    ardInstDefault = " (Default : " + ardInst + ")"

print "Please Enter Arduino Installation Directory" + ardInstDefault + " :"

ardInstCustom = raw_input()

if os.path.isdir(ardInstCustom) :
    ardInst = ardInstCustom

print ardInst

#Initialize All Variables Required To Upload The Code

mst_brdPkg = "arduino"
mst_brdArch = "avr"
mst_brdBrd = "uno"
mst_cfgFile = os.path.join(ardInst, "hardware/tools/avr/etc/avrdude.conf")
mst_partNo = "atmega328p"
mst_progmr = "arduino"
mst_port = "/dev/ttyUSB0"
mst_baud = "115200"
mst_code = os.path.join(selfPath, "../masterCode/masterCode.ino")
mst_hex = os.path.join(mst_bldDir, mst_code + ".hex")

slv_brdPkg = "attiny"
slv_brdArch = "avr"
slv_brdBrd = "ATtinyX5"
slv_brdParam-cpu = "attiny85"
slv_brdParam-clk = "internal8"
slv_cfgFile = os.path.join(ardInst, "hardware/tools/avr/etc/avrdude.conf")
slv_partNo = "attiny85"
slv_progmr = "stk500v1"
slv_port = "/dev/ttyUSB0"
slv_baud = "19200"
slv_code = os.path.join(selfPath, "../slaveCode/slaveCode.ino")
slv_hex = os.path.join(mst_bldDir, mst_code + ".hex")



