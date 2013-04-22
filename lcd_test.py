#!/usr/bin/env python
#
# Test Script to control Keg LCD
#
#
#
import sys, os
from time import sleep

class LCDdisplay(object):
    """
    This is a display class, holding methods to
    write chars to an HDD44780 LCD display. Most of this LCD
    code was taken or modified from the Adafruit git repo:
      git://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
    """
    # commands
    LCD_CLEARDISPLAY        = 0x01
    LCD_RETURNHOME          = 0x02
    LCD_ENTRYMODESET        = 0x04
    LCD_DISPLAYCONTROL      = 0x08
    LCD_CURSORSHIFT         = 0x10
    LCD_FUNCTIONSET         = 0x20
    LCD_SETCGRAMADDR        = 0x40
    LCD_SETDDRAMADDR        = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT          = 0x00
    LCD_ENTRYLEFT           = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON           = 0x04
    LCD_DISPLAYOFF          = 0x00
    LCD_CURSORON            = 0x02
    LCD_CURSOROFF           = 0x00
    LCD_BLINKON             = 0x01
    LCD_BLINKOFF            = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE         = 0x08
    LCD_CURSORMOVE          = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE         = 0x08
    LCD_CURSORMOVE          = 0x00
    LCD_MOVERIGHT           = 0x04
    LCD_MOVELEFT            = 0x00

    # flags for function set
    LCD_8BITMODE            = 0x10
    LCD_4BITMODE            = 0x00
    # LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
    # LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
    # LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
    # LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line 
    LCD_3LINE               = 0x94
    LCD_2LINE               = 0x08
    LCD_1LINE               = 0x00
    LCD_5x10DOTS            = 0x04
    LCD_5x8DOTS             = 0x00

    def __init__(self, pin_rs=25, pin_e=24, pins_db=[23, 17, 27, 22], GPIO = None):
        #For the above default varaibles, I am writing for a #2 RaspPi. So,
        #pin 21 was changed to pin 27.

        # Emulate the old behavior of using RPi.GPIO if we haven't been given
        # an explicit GPIO interface to use
        if not GPIO:
            import RPi.GPIO as GPIO
        
        self.GPIO = GPIO
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(self.pin_e, GPIO.OUT)
        self.GPIO.setup(self.pin_rs, GPIO.OUT)

        for pin in self.pins_db:
            self.GPIO.setup(pin, GPIO.OUT)

        self.write4bits(0x33) # initialization
        self.write4bits(0x32) # initialization
        self.write4bits(0x28) # 2 line 5x7 matrix
        self.write4bits(0x0C) # turn cursor off 0x0E to enable cursor
        self.write4bits(0x06) # shift cursor right
        
        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        
        self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
        self.displayfunction |= self.LCD_2LINE
        
        # Initialize to default text direction (for romance languages)
        self.displaymode =  self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode) #  set the entry mode
        
        self.clear()

    def clear(self):
        self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
        self.delayMicroseconds(3000)    # 3000 microsecond sleep, clearing the display takes a long time

    def write4bits(self, bits, char_mode=False):
        """ Send command to LCD """

        self.delayMicroseconds(1000) # 1000 microsecond sleep
        bits=bin(bits)[2:].zfill(8)
        self.GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            self.GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i], True)

        self.pulseEnable()

        for pin in self.pins_db:
            self.GPIO.output(pin, False)

        for i in range(4,8):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i-4], True)

        self.pulseEnable()

    def delayMicroseconds(self, microseconds):
        seconds = microseconds / float(1000000) # divide microseconds by 1 million for seconds
        sleep(seconds)

    def pulseEnable(self):
        self.GPIO.output(self.pin_e, False)
        self.delayMicroseconds(1)       # 1 microsecond pause - enable pulse must be > 450ns 
        self.GPIO.output(self.pin_e, True)
        self.delayMicroseconds(1)       # 1 microsecond pause - enable pulse must be > 450ns 
        self.GPIO.output(self.pin_e, False)
        self.delayMicroseconds(1)       # commands need > 37us to settle

    def message(self, text):
        """
        Send a string to the LCD screen. A newline bumps
        to the next line of the LCD.
        """
        for char in text:
            if char == '\n':
                self.write4bits(0xC0) # next line
            else:
                self.write4bits(ord(char),True)


