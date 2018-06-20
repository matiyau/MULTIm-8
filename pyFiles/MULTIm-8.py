import os

#Function To Write Code For Master To Activate One IC At A Time
def mst_codeEdit(mst_codeFile, ICnum) :
    slv_selectPins = ["A0", "A1", "A2", ["A3", "A4"]]

    #Read The Master Code File
    mstCode = open(mst_codeFile, "r")
    mstLines = mstCode.read().splitlines()
    mstCode.close()
    
    #Start Line Of Block To Be Inserted In Master Code
    mst_pinSetup = ["// MULTIm-8 Starts Here"]

    #Construct The pinMode And digitalWrite Block
    for pin in slv_selectPins[:3] :
        pinMode = "pinMode(" + pin + ", OUTPUT);"
        digitalWrite = "digitalWrite(" + pin + ", " + str(ICnum%2) + ");"
        mst_pinSetup.append(pinMode)
        mst_pinSetup.append(digitalWrite)
        ICnum = ICnum/2
        
    for pin in slv_selectPins[3] :
        pinMode = "pinMode(" + pin + ", OUTPUT);"
        digitalWrite = "digitalWrite(" + pin + ", " + str(ICnum) + ");"
        mst_pinSetup.append(pinMode)
        mst_pinSetup.append(digitalWrite)
        ICnum = int(not ICnum)    

    #End Line Of Block To Be Inserted In Master Code
    mst_pinSetup.append("// MULTIm-8 Ends Here")

    #Remove Any Previous MULTIm-8 Block From The Master Code
    MULTIm8_Start = 0
    MULTIm8_End = 0
    for i in range (0,len(mstLines)) :
        if "// MULTIm-8 Starts Here" in mstLines[i] :
            MULTIm8_Start = i
            break
    for i in range (0,len(mstLines)) :
        if "// MULTIm-8 Ends Here" in mstLines[i] :
            MULTIm8_End = i
            break
    mstLines = mstLines[:MULTIm8_Start] + mstLines[MULTIm8_End + 1:]
    
    
    #Find void setup Function in The Code
    for i in range (0,len(mstLines)) :
        if mstLines[i][:10] == "void setup" :
            for pinSetup in mst_pinSetup :
                mstLines[i] = mstLines[i] + "\n" + pinSetup
            break

    #Write To The Master Code File
    mstCode = open(mst_codeFile, "w")
    for line in mstLines :
        mstCode.write(line + '\n')
    mstCode.close()
    

#Function To Write Code For Slave To Assign Unique ID
def slv_codeEdit(slv_codeFile, UID) :
    #Read The Slave Code File
    slvCode = open(slv_codeFile, "r")
    slvLines = slvCode.read().splitlines()
    slvCode.close()

    #Find "#define UID" Line
    for i in range (0, len(slvLines)) :
        if slvLines[i][:11] == "#define UID" :
            slvLines[i] = "#define UID " + str(UID)

    #Write To The Slave Code File
    slvCode = open(slv_codeFile, "w")
    for line in slvLines :
        slvCode.write(line + '\n')
    slvCode.close()    

        

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
mst_code = os.path.join(selfPath, "../masterCode/masterCode.ino")
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
slv_code = os.path.join(selfPath, "../slaveCode/slaveCode.ino")
slv_hex = os.path.join(slv_bldDir, "slaveCode.ino.hex")

#Common Variables
cfgFile = os.path.join(ardInst, "hardware/tools/avr/etc/avrdude.conf")
compOpts = " --verify --preserve-temp-files --verbose"

#Terminal Commands For Compilation And Upload Of Code To Master
mst_compile = os.path.join(ardInst, "arduino") + compOpts + " --board " + mst_board + " --pref build.path=" + mst_bldDir + " " + '"' + mst_code + '"'
mst_upload = os.path.join(ardInst, "hardware/tools/avr/bin/avrdude") + " -C " + cfgFile + " -v -p " + mst_partNo + " -c " + mst_progmr + " -P " + mst_port + " -b " + mst_baud + " -D -Uflash:w:/tmp/MULTIm-8_Uno/masterCode.ino.hex:i"

#Terminal Commands For Compilation Of Code, Burning Of Bootloader And Upload Of Code To Slave
slv_compile = os.path.join(ardInst, "arduino") + compOpts + " --board " + slv_board + " --pref build.path=" + slv_bldDir + " " + '"' + slv_code + '"'
slv_bootloader = os.path.join(ardInst, "hardware/tools/avr/bin/avrdude") + " -C " + cfgFile + " -v -v -v -v -p " + slv_partNo + " -c " + slv_progmr + " -P " + slv_port + " -b " + slv_baud + " -e -Uefuse:w:0xff:m -Uhfuse:w:0xdf:m -Ulfuse:w:0xe2:m"
slv_upload = os.path.join(ardInst, "hardware/tools/avr/bin/avrdude") + " -C " + cfgFile + " -v -p " + slv_partNo + " -c " + slv_progmr + " -P " + slv_port + " -b " + slv_baud + " -Uflash:w:/tmp/MULTIm-8_ATtiny85/slaveCode.ino.hex:i"

#Input The Index Of Starting Slot For Batch Programming
ICstart = 0
print "Please Enter The Index Of Starting IC Slot [Default - 0] :"
attempts = 5
while True:
    ICstartCus = raw_input()
    if ICstartCus == '' :
        break
    elif ICstartCus.isdigit() and int(ICstartCus)>=0 and int(ICstartCus)<=15 :
        ICstart = int(ICstartCus)
        break
    else :
        attempts = attempts-1
        if attempts :
            print "Invalid Input. Please Enter An Integer From 0 To 15. Leave Blank For Default."
        else :
            print "Too Many Attempts. Proceeding With Default Value (Slot 0)."
            ICcount = ICcountCus
            break

#Input The Number Of ICs For Batch Programming
ICcount = 16 - ICstart
print "Please Enter The Number Of ICs To Program :\n(Max - " + str(ICcount) + ", Min - 1) [Default - " + str(ICcount) + "]"
attempts = 5
while True:
    ICcountCus = raw_input()
    if ICcountCus == '' :
        break
    elif ICcountCus.isdigit() and int(ICcountCus)>0 and int(ICcountCus)<17 :
        ICcount = int(ICcountCus)
        break
    else :
        attempts = attempts-1
        if attempts :
            print "Invalid Input. Please Enter An Integer From 1 To 16. Leave Blank For Default."
        else :
            print "Too Many Attempts. Proceeding With Default Value (16 ICs)."
            ICcount = ICcountCus
            break

#Input The Start UID For Batch Programming
UIDstart = 0
print "Please Enter The Starting UID Of ICs To Program [Default - 0] :"
attempts = 5
while True:
    UIDstartCus = raw_input()
    if UIDstartCus == '' :
        break
    elif UIDstartCus.isdigit() :
        UIDstart = int(UIDstartCus)
        break
    else :
        attempts = attempts-1
        if attempts :
            print "Invalid Input. Please Enter An Integer. Leave Blank For Default."
        else :
            print "Too Many Attempts. Proceeding With Default Value (Start UID - 0)."
            UIDstart = UIDstartCus
            break

for i in range(0, ICcount) :
    mst_codeEdit(mst_code, i)
    slv_codeEdit(slv_code, UIDstart + i)

    print "\nIC : " + str(i) + ", UID : " + str(UIDstart + i)
        
    #Compile Code For Master
    mst_cmplRslt = os.system(mst_compile)
    if mst_cmplRslt :
        print "Compilation For Master Failed With Error Code : " + str(mst_cmplRslt)
        exit()
    print "Compiled Code For Master"

    #Upload Code To Master
    mst_upldRslt = os.system(mst_upload)
    if mst_upldRslt :
        print "Upload To Master Failed With Error Code : " + str(mst_upldRslt)
        exit()
    print "Uploaded HEX To Master"

    #Compile Code For Slave
    slv_cmplRslt = os.system(slv_compile)
    if slv_cmplRslt :
        print "Compilation For Slave Failed With Error Code : " + str(slv_cmplRslt)
        exit()
    print "Compiled Code For Slave"

    #Burn BootLoader To Slave
    slv_btldRslt = os.system(slv_bootloader)
    if slv_btldRslt :
        print "Burning Of Bootloader To Slave Failed With Error Code : " + str(slv_btldRslt)
        exit()
    print "Bootloader Burnt To Slave"

    #Upload Code To Slave
    slv_upldRslt = os.system(slv_upload)
    if slv_upldRslt :
        print "Upload To Slave Failed With Error Code : " + str(slv_upldRslt)
        exit()
    print "Uploaded HEX To Slave"
