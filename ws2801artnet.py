import time
from signal import signal, SIGINT
from sys import exit
from ola.ClientWrapper import ClientWrapper
import RPi.GPIO as GPIO
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI


# Configure the count of pixels:
PIXEL_COUNT = 216

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

REFRESH_RATE = 30  # in hz
REFRESH_DELAY=int(1000/30)
pixels_array = [[0] * int(PIXEL_COUNT/2)*3,[0] * int(PIXEL_COUNT/2)*3] #RGB values to 0 N times

wrapper = None
t_start=time.time()
frame_counter=0
def NewDataUniverse1(data):
    pixels_array[0]=data

def NewDataUniverse2(data):
    pixels_array[1]=data

def updatePixels():
    global wrapper, t_start, frame_counter
    if time.time()-t_start>10: #every 10 seconds display FPS
        print("FPS:",frame_counter/(time.time()-t_start))
        t_start=time.time()
        frame_counter=0
    frame_counter+=1
    #print(pixels_array[0][0],pixels_array[1][0])
    wrapper.AddEvent(REFRESH_DELAY, updatePixels)
    index_list=range(0,int(PIXEL_COUNT/2)*3)
    one_of_three=list(filter(lambda x: x%3==0, index_list))
    for i,x in enumerate(one_of_three):
        rgb_values=pixels_array[0]
        color=Adafruit_WS2801.RGB_to_color(rgb_values[x],rgb_values[x+1],rgb_values[x+2])
        pixels.set_pixel(i,color)
    for i,x in enumerate(one_of_three):
        rgb_values=pixels_array[1]
        color=Adafruit_WS2801.RGB_to_color(rgb_values[x],rgb_values[x+1],rgb_values[x+2])
        pixels.set_pixel(int(PIXEL_COUNT/2)+i,color)
    # for i in range(PIXEL_COUNT):
    #     index =  0 if(i<PIXEL_COUNT/2) else 1
    #     index2=i%PIXEL_COUNT
    #     c=Adafruit_WS2801.RGB_to_color(pixels_array[index][index2*3],pixels_array[index][index2*3+1],pixels_array[index][index2*3+2])
    #     pixels.set_pixel(i,c)
    pixels.show()


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    pixels.clear()
    wrapper.Stop()
    exit(0)


if __name__ == "__main__":
    signal(SIGINT, handler)
    # Clear all the pixels to turn them off.
    pixels.clear()
    pixels.show()
    wrapper = ClientWrapper()
    client = wrapper.Client()
    #client2 = wrapper.Client()
    client.RegisterUniverse(1, client.REGISTER, NewDataUniverse1)
    client.RegisterUniverse(2, client.REGISTER, NewDataUniverse2)
    #client2.RegisterUniverse(1, client1.REGISTER, NewDataUniverse1)
    wrapper.AddEvent(REFRESH_DELAY, updatePixels)
    wrapper.Run()


####### FUCCCK MONKEY PATCH FILE OR INSTALL VERSION 0.10.8
# /home/pi/.local/lib/python3.7/site-packages/ola/ClientWrapper.py

#
# class _Event(object):
#   """An _Event represents a timer scheduled to expire in the future.
#   Args:
#     delay: datetime.timedelta or number of ms before this event fires
#     callback: the callable to run
#   """
#   def __init__(self, delay, callback):
#     self._run_at = (datetime.datetime.now() +
#                     (delay if isinstance(delay, datetime.timedelta)
#                      else datetime.timedelta(milliseconds=delay)))
#     self._callback = callback
#
#   def __eq__(self, other):
#     if not isinstance(other, self.__class__):
#       return False
#     return self._run_at == other._run_at and self._callback == other._callback
#
#   def __lt__(self, other):
#     if not isinstance(other, self.__class__):
#       return NotImplemented
#     if self._run_at != other._run_at:
#       return self._run_at < other._run_at
#     return self._callback.__name__ < other._callback.__name__
#
#   # These 4 can be replaced with functools:total_ordering when 2.6 is dropped
#   def __le__(self, other):
#     if not isinstance(other, self.__class__):
#       return NotImplemented
#     return self < other or self == other
#
#   def __gt__(self, other):
#     if not isinstance(other, self.__class__):
#       return NotImplemented
#     return not self <= other
#
#   def __ge__(self, other):
#     if not isinstance(other, self.__class__):
#       return NotImplemented
#     return not self < other
#
#   def __ne__(self, other):
#     return not self == other
#
#   def __hash__(self):
#     return hash((self._run_at, self._callback))
#
#   def TimeLeft(self, now):
#     """Get the time remaining before this event triggers.
#     Returns:
#       The number of seconds (as a float) before this event fires.
#     """
#     time_delta = self._run_at - now
#     seconds = time_delta.seconds + time_delta.days * 24 * 3600
#     seconds += time_delta.microseconds / 10.0 ** 6
#     return seconds
#
#   def HasExpired(self, now):
#     """Return true if this event has expired."""
#     return self._run_at < now
#
#   def Run(self):
#     """Run the callback."""
#     self._callback()
