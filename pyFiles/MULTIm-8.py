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

#Variables For Master (Programmer)
mst_brdPkg = "arduino"
mst_brdArch = "avr"
mst_brdBrd = "uno"
mst_board = mst_brdPkg + ":" + mst_brdArch + ":" + mst_brdBrd
mst_partNo = "atmega328p"
mst_progmr = "arduino"
mst_port = "/dev/ttyUSB0"
mst_baud = "115200"
mst_code = '"' + os.path.join(selfPath, "../masterCode/masterCode.ino") + '"'
mst_hex = os.path.join(mst_bldDir, "masterCode.ino.hex")

#Variables For Slave (Chip To Be Programmed)
slv_brdPkg = "attiny"
slv_brdArch = "avr"
slv_brdBrd = "ATtinyX5"
slv_brdParam_cpu = "attiny85"
slv_brdParam_clk = "internal8"
slv_board = slv_brdPkg + ":" + slv_brdArch + ":" + slv_brdBrd + ":cpu=" + slv_brdParam_cpu + ",clock=" + slv_brdParam_clk
slv_partNo = "attiny85"
slv_progmr = "stk500v1"
slv_port = "/dev/ttyUSB0"
slv_baud = "19200"
slv_code = '"' + os.path.join(selfPath, "../slaveCode/slaveCode.ino") + '"'
slv_hex = os.path.join(slv_bldDir, "slaveCode.ino.hex")

#Common Variables
cfgFile = os.path.join(ardInst, "hardware/tools/avr/etc/avrdude.conf")
compOpts = " --verify --preserve-temp-files --verbose"

#Terminal Commands For Compilation And Upload Of Code To Master
mst_compile = os.path.join(ardInst, "arduino") + compOpts + " --board " + mst_board + " --pref build.path=" + mst_bldDir + " " + mst_code
mst_upload = os.path.join(ardInst, "hardware/tools/avr/bin/avrdude") + " -C " + cfgFile + " -v -p " + mst_partNo + " -c " + mst_progmr + " -P " + mst_port + " -b " + mst_baud + " -D -Uflash:w:/tmp/MULTIm-8_Uno/masterCode.ino.hex:i"

#Terminal Commands For Compilation Of Code, Burning Of Bootloader And Upload Of Code To Slave
slv_compile = os.path.join(ardInst, "arduino") + compOpts + " --board " + slv_board + " --pref build.path=" + slv_bldDir + " " + slv_code
slv_bootloader = os.path.join(ardInst, "hardware/tools/avr/bin/avrdude") + " -C " + cfgFile + " -v -v -v -v -p " + slv_partNo + " -c " + slv_progmr + " -P " + slv_port + " -b " + slv_baud + " -e -Uefuse:w:0xff:m -Uhfuse:w:0xdf:m -Ulfuse:w:0xe2:m"
slv_upload = os.path.join(ardInst, "hardware/tools/avr/bin/avrdude") + " -C " + cfgFile + " -v -p " + slv_partNo + " -c " + slv_progmr + " -P " + slv_port + " -b " + slv_baud + " -Uflash:w:/tmp/MULTIm-8_ATtiny85/slaveCode.ino.hex:i"

#Compile Code For Master
mst_cmplRslt = os.system(mst_compile)
if mst_cmplRslt :
    print "Compilation For Master Failed With Error Code : " + str(mst_cmplRslt)
    exit()
print "Compilation For Master Successful."

#Upload Code To Master
mst_upldRslt = os.system(mst_upload)
if mst_upldRslt :
    print "Upload To Master Failed With Error Code : " + str(mst_upldRslt)
    exit()
print "Upload To Master Successful."

#Compile Code For Slave
slv_cmplRslt = os.system(slv_compile)
if slv_cmplRslt :
    print "Compilation For Slave Failed With Error Code : " + str(slv_cmplRslt)
    exit()
print "Compilation For Slave Successful."

#Burn BootLoader To Slave
slv_btldRslt = os.system(slv_bootloader)
if slv_btldRslt :
    print "Burning Bootloader To Slave Failed With Error Code : " + str(slv_btldRslt)
    exit()
print "Burning Bootloader To Slave Successful."

#Upload Code To Slave
slv_upldRslt = os.system(slv_upload)
if slv_upldRslt :
    print "Upload To Slave Failed With Error Code : " + str(slv_upldRslt)
    exit()
print "Upload To Slave Successful."
