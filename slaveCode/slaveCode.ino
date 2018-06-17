/*
 * Project          : IRis
 * Purpose          : HackFest 2018 - The Annual 36 Hour Hackathon At IIT (ISM) Dhanbad
 * Module           : Slave (Remote)
 ---------------------------------------------------------------------------------------
 * Microcontroller  : ATtiny85
 * IR Demodulator   : VS1838B
 * Programmer       : Arduino Uno R3 as ISP
 * Library          : tiny_IRremote (For IR Communication on ATtiny Series)
 * IDE              : Arduino IDE 1.8.4 On Ubuntu 16.04 LTS
 ---------------------------------------------------------------------------------------
 * Author           : Nishad Mandlik
 * Organization     : RoboISM - The Robotics Club Of IIT (ISM) Dhanbad
 * 
 */


//  Pin 1 (Reset)         : Unused
//  Pin 2 (GPIO-3/ANLG-3) : User-Input
//  Pin 3 (GPIO-4/ANLG-2) : IR Tx
//  Pin 4                 : GND
//  Pin 5 (GPIO-0/AREF)   : GND
//  Pin 6 (GPIO-1)        : Red LED
//  Pin 7 (GPIO-2/ANLG-1) : IR Rx
//  Pin 8                 : +Vcc

#include <tiny_IRremote.h>
#define UID 1
#define LED_RED 1
#define OPT_IP A3

uint16_t usrIp = 0;
unsigned int irOut[] = {5000, 2500, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 500};

struct irCmd {
  byte address: 6;
  byte opcode: 2;
}irQuery;

IRsend irtx; //Library Object to Send IR Signals
IRrecv irrx(2); //Library Objet to Receive IR Signals

decode_results irIn;

uint8_t decodeRaw() {
  //Signal Is Present In Ticks Of 50uS.

  //First HIGH Pulse : 5000 (3500 to 6500)
  if (irIn.rawbuf[1]<70 && irIn.rawbuf[1]>130) {
    return 1;
  }
  
  //First LOW Pulse : 2500 (1500 to 3500)
  if (irIn.rawbuf[2]<30 && irIn.rawbuf[2]>70) {
    return 2;
  }

  //End HIGH Pulse : 500 (250 To 750)
  if (irIn.rawbuf[19]<5 && irIn.rawbuf[19]>15) {
    return 3;
  }

  //First 6 bits (Address)
  for (uint8_t i=3; i<15; i+=2) {    
    irQuery.address = irQuery.address<<1;
    if (irIn.rawbuf[i]>irIn.rawbuf[i+1]) {
      //High
      irQuery.address = irQuery.address | 0b00000001;
    }
    else if (irIn.rawbuf[i]<irIn.rawbuf[i+1]) {
      //Low
      irQuery.address = irQuery.address & 0b11111110;
    }
    else {
      return 4;
    }
  }

  //Last 2 bits (Instruction)
  for (uint8_t i=15; i<19; i+=2) {      
    irQuery.opcode = irQuery.opcode<<1;
    if (irIn.rawbuf[i]>irIn.rawbuf[i+1]) {
      //High
      irQuery.opcode = irQuery.opcode | 0b00000001;
    }
    else if (irIn.rawbuf[i]<irIn.rawbuf[i+1]) {
      //Low
      irQuery.opcode = irQuery.opcode & 0b11111110;
    }
    else {
      return 5;
    }
  }
  return 0;
}


void setup() {
  ADMUX = ADMUX & 0b00111111; //Set REFS1=0 And REFS0=0 To Set Analog Reference (AREF) To Vcc.
  
  /*

  better to create new code. keep this one for old devices
  Analog user input pulled up.
  comparator negative = 2.56 or vcc from pin 5
  adc value left align and read only upper byte. forget two lsbs
  
   
  MCUCR = MCUCR | 0b00100000; //Set The SE (Sleep Enable) Bit in MCUCR

  //Select Sleep Mode As IDLE
  //Set SM1 Bit, Reset SM0 Bit
  MCUCR = MCUCR | 0b00010000;
  MCUCR = MCUCR & 0b11110111;

  //Turn Off USI, Timer0 & ADC
  PRR = PRR | 0b00000111;

  //Set PCIE (PinChange Interrupt Enable) Bit in GIMSK (General Interrupt Mask Registered)
  GIMSK = GIMSK | 0b00100000;

  //Enable PinChange Interrupt For GPIO 


  sreg interrupt enable
GIMSK enable pin change (PCIE)
enable pin change interrupt on selected pins in pcmsk
  
   */
  for (uint8_t i = 6; i>=1; i--)
  {
    if ((UID>>(6-i)) & 0b1) {
      //When bit is 1
      irOut[2*i] = 1000;
      irOut[2*i + 1] = 500;
    }
    else {
      //When bit is 0
      irOut[2*i] = 500;
      irOut[2*i + 1] = 1000;
    } 
  }
  pinMode(LED_RED, OUTPUT);
  pinMode(OPT_IP, INPUT);
  irrx.enableIRIn(); // Start the receiver
  digitalWrite(LED_RED, HIGH);
  delay(50);
  digitalWrite(LED_RED, LOW);
}

void loop() {
  //MSB Of usrIp Is Used As Input Acceptance Flag.
  //If It Is RESET, New Inputs Would Be Taken And irOut Data Will Be Changed Accordingly.
  //If It Is SET, New Inputs Would Be Taken But The Change Would Not Be Reflected In "irOut".
  usrIp = (usrIp & 0x8000) | analogRead(OPT_IP);

  //When MSB Of usrIp Is 1, None Of The Following Conditions Are Satisfied.
  //So, No Changes Are Made To "irOut".
  if (usrIp<128) {
    //~0 - Option D  [11]    
    irOut[14] = 1000;
    irOut[15] = 500;
    irOut[16] = 1000;
    irOut[17] = 500;
    digitalWrite(LED_RED, HIGH);
    delay(50);
    digitalWrite(LED_RED, LOW);
  }
  else if (usrIp>128 && usrIp<384) {
    //~256 - Option C [10]
    irOut[14] = 1000;
    irOut[15] = 500;
    irOut[16] = 500;
    irOut[17] = 1000;
    digitalWrite(LED_RED, HIGH);
    delay(50);
    digitalWrite(LED_RED, LOW);
  }
  else if (usrIp>384 && usrIp<640) {
    //~512 - Option B [01]
    irOut[14] = 500;
    irOut[15] = 1000;
    irOut[16] = 1000;
    irOut[17] = 500;
    digitalWrite(LED_RED, HIGH);
    delay(50);
    digitalWrite(LED_RED, LOW);
  }
  else if (usrIp>640 && usrIp<896) {
    //~768 - Option A [00]
    irOut[14] = 500;
    irOut[15] = 1000;
    irOut[16] = 500;
    irOut[17] = 1000;
    digitalWrite(LED_RED, HIGH);
    delay(50);
    digitalWrite(LED_RED, LOW);
  }
  
  if (!(irrx.decode(&irIn))) {
    return;
  }

  if (!decodeRaw()) {
    if (irQuery.opcode == 0b00 && (irQuery.address == 0 || irQuery.address == UID)) {
      //OpCode 00 : Stop Input
      usrIp = usrIp | 0x8000;
      digitalWrite(LED_RED, HIGH);
    }
    else if ((irQuery.opcode == 0b01 || irQuery.opcode == 0b10) && irQuery.address == UID) {
      //OpCode 01 : Ping
      //OpCode 10 : Send Input
      
      //Send The Encoded Signal
      irtx.sendRaw(irOut, sizeof(irOut) / sizeof(irOut[0]), 38);
      
      //Re-Enable The Receiver
      irrx.enableIRIn();
      
      //Start Accepting User-Input
      usrIp = 0;
      
      //Reset The Data Part Of "irOut" To Blank Response (No Button Pressed)
      irOut[14] = 750;
      irOut[15] = 750;
      irOut[16] = 750;
      irOut[17] = 750;
      digitalWrite(LED_RED, LOW);
    }
    else if (irQuery.opcode == 0b11 && (irQuery.address == 0 || irQuery.address == UID)) {
      //OpCode 11 : Reset Input

      //Reset The Data Part Of "irOut" To Blank Response (No Button Pressed)
      irOut[14] = 750;
      irOut[15] = 750;
      irOut[16] = 750;
      irOut[17] = 750;
      digitalWrite(LED_RED, LOW);
    }
  }
  
  //Accept Next IR Data
  irrx.resume();   
    
}
