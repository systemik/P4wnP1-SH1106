#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import subprocess
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib

from luma.oled.device import sh1106

# Input pins:
L_pin = 5
R_pin = 26
P_pin = 13
U_pin = 6
D_pin = 19

A_pin = 21
B_pin = 20
C_pin = 16


#GPIO definition for reference
RST_PIN        = 25
CS_PIN         = 8
DC_PIN         = 24
KEY_UP_PIN     = 6
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

GPIO.setmode(GPIO.BCM)

GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(P_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

RST = 25
DC = 24
SPI_PORT = 0
SPI_DEVICE = 0

serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC, gpio_RST = RST)
device = sh1106(serial, rotate=2) #sh1106

width = 128
height = 64

image = Image.new('1', (width, height))

draw = ImageDraw.Draw(image)
draw.rectangle((0,0,width,height), outline=0, fill=0)

font = ImageFont.load_default()

x = 0
top = -2

def system_shutdown(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 with canvas(device) as draw:
     draw.rectangle((0,0,width,height), outline=0, fill=0)
     draw.text((x, top), "Shutdown P4wnP1",font=font, fill=255)
     draw.text((x, top+24), "to activate payload?",font=font, fill=255)
     draw.text((x, top+48), "Yes / No",font=font, fill=255)

 try:
  while 1:

   if not GPIO.input(A_pin):
    with canvas(device) as draw:
        draw.rectangle((0,0,width,height), outline=0, fill=0)
    cmd = "sudo shutdown -h now"
    cmdout = subprocess.check_output(cmd, shell = True )

   if not GPIO.input(B_pin):
    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

  time.sleep(.18)

 except KeyboardInterrupt:
  GPIO.cleanup()

def activate_payload(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 # comment out active payload
 cmd = "sed -i -e '/^PAYLOAD=/s/^PAYLOAD=/#PAYLOAD=/' /home/pi/P4wnP1/setup.cfg"
 cmdout = subprocess.check_output(cmd, shell = True )

 # activate payload
 cmd = "sed -i -e '/#PAYLOAD=" + payloads[pos_in_payloads+menu_cursor_pos] + "/s/#PAYLOAD=/PAYLOAD=/' /home/pi/P4wnP1/setup.cfg"
 cmdout = subprocess.check_output(cmd, shell = True )

 system_shutdown(max_row,payloads,pos_in_payloads,menu_cursor_pos)

def select_payload(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 with canvas(device) as draw:
     draw.rectangle((0,0,width,height), outline=0, fill=0)
     draw.text((x, top), "Activate Payload ?",font=font, fill=255)
     draw.text((x, top+24), payloads[pos_in_payloads+menu_cursor_pos],font=font, fill=255)
     draw.text((x, top+48), "Yes / No",font=font, fill=255)

 try:
  while 1:
   if not GPIO.input(A_pin):
    activate_payload(max_row,payloads,pos_in_payloads,menu_cursor_pos)

   if not GPIO.input(B_pin):
    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

  time.sleep(.18)

 except KeyboardInterrupt:
  GPIO.cleanup()

def draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 with canvas(device) as draw:
     draw.rectangle((0,0,width,height), outline=0, fill=0)
     draw.text((x, top), "Select Payload",font=font, fill=255)
     z = 0
     for i in payloads:
      if z > max_row - 1: # end of screen
       break
      if z + pos_in_payloads > len(payloads)-1: # end of payload list
       break
      if z == menu_cursor_pos:
       draw.text((x, top+12+(z*8)), ">" + payloads[z+pos_in_payloads],font=font, fill=255)
      else:
       draw.text((x, top+12+(z*8)), " " + payloads[z+pos_in_payloads],font=font, fill=255)
      z += 1

 #disp.image(image)
 #disp.display()
 buttons(max_row,payloads,pos_in_payloads,menu_cursor_pos)

# only up / down / center used
def buttons(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 try:
  while 1:
   if not GPIO.input(U_pin):
    menu_cursor_pos -= 1

    if menu_cursor_pos < 0: # check if cursor is on top
     if pos_in_payloads > max_row -1: # check if we not on page 1
      pos_in_payloads -= max_row
      menu_cursor_pos = max_row -1
     else: # we are on top on page 1
      menu_cursor_pos = 0

    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

   if not GPIO.input(D_pin):
    if pos_in_payloads + menu_cursor_pos != len(payloads)-1: # check if we are at the end of payloads
      menu_cursor_pos += 1

    if menu_cursor_pos > max_row -1 : # if cursor is at end of screnn jump to next page
     pos_in_payloads += max_row
     menu_cursor_pos = 0

    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

   if not GPIO.input(P_pin):
    select_payload(max_row,payloads,pos_in_payloads,menu_cursor_pos)

   time.sleep(.18)

 except KeyboardInterrupt:
  GPIO.cleanup()

if __name__ == '__main__':
 # get list of payloads
 cmd = "cat /home/pi/P4wnP1/setup.cfg | grep 'PAYLOAD' |  grep -o '^[^#]*#\?[^#]*' | awk -F '=' '{print $2}' | awk -F '.' '{print $1}'"
 cmdout = subprocess.check_output(cmd, shell = True )
 payloads = cmdout.splitlines()
 max_row = 6
 menu_cursor_pos = 0
 pos_in_payloads = 0

 draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)
