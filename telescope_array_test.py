from __future__ import division
import time
import numpy as np
import Adafruit_DHT
import RPi.GPIO as GPIO
import Adafruit_PCA9685

#all telescope positions used are numpy arrays of the form [RA, Dec]
#telescopes 0 to 3 correspond to the real telescopes. Telescope 4 means no telescope is active.


#Defining the telescope servo and sensor locations
# RA, Dec, button, temp/humid, Red LED, Green LED,
pins = np.array([[4, 5, 18, 25, 0, 0], #telescope 0
                [6, 7, 12, 23, 0, 0], #telescope 1
                [8, 9, 13, 22, 0, 0], #telescope 2
                [10, 11, 6, 24, 0, 0]]) #telescope 3
                

#setting up buttons on the correct pins
GPIO.setmode(GPIO.BCM) #using BCM pin names

#Setting up inputs on buttons
GPIO.setup(pins[0,2], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pins[1,2], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pins[2,2], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pins[3,2], GPIO.IN, pull_up_down=GPIO.PUD_UP)

#setting up outputs for LEDS
##GPIO.setup(pins[0,4],GPIO.OUT)
##GPIO.setup(pins[1,4],GPIO.OUT)
##GPIO.setup(pins[2,4],GPIO.OUT)
##GPIO.setup(pins[3,4],GPIO.OUT)
##GPIO.setup(pins[0,5],GPIO.OUT)
##GPIO.setup(pins[1,5],GPIO.OUT)
##GPIO.setup(pins[2,5],GPIO.OUT)
##GPIO.setup(pins[3,5],GPIO.OUT)

#setting up the pulse width modulation controller for the servos
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)


    

def main_function():
    '''The function used to constantly check the sensors and update the telelscope
    accordingly'''

    #defining the park position and a random target to observe
    park = np.ones(2) 
    telescope_posn = np.array([np.random.randint(30,80), np.random.randint(0,180)])

    current_telescope = 4 #no telescope is currently active - 4 means no telescope
    track_counter = 0 #counter used for tracking
    
    binary_values, comparitive_values = get_sensors(np.zeros((4,2))) #temp/humidity values
    print(binary_values)
    print(comparitive_values)
    #temp/humidity are compared to the values measured on startup - consider changing this
    #to values measured every few minutes if code will run for a long time.
    
    #infinite loop - consided putting in break??
    while True:
        new_telescope, good_telescopes, bad_telescopes = find_best_telescope(comparitive_values)
        #update_leds(good_telescopes, bad_telescopes)
        #changing to the new telescope if current telescope has triggered sensor
        if new_telescope != current_telescope:
            move_telescope(current_telescope, park)
            move_telescope(new_telescope, telescope_posn)
            current_telescope = new_telescope

        #tracking - moves the telescope by a degree every 20 loops of the code
        if track_counter > 20:
            new_posn = telescope_posn[0], telescope_posn[1]+1
            move_telescope(current_telescope, new_posn)
            telescope_posn = new_posn
            track_counter = 0
        else:
            track_counter +=1
        
        time.sleep(20) #sleep for 1 second before looping
        
    return True


def find_best_telescope(comparitive_values):
    '''A function for finding the best telescope. The first telescope
    with no triggered sensors is selected. The value returned corresponds
    to this telescope. A value of 4 signifies no telescope without a
    triggered sensor exists'''
    sensor_status, unused_comparitives = get_sensors(comparitive_values)
    sensor_status_sums = np.sum(sensor_status, axis = 1)
    good_telescopes = np.where(sensor_status_sums == 0)
    bad_telescopes = np.where(sensor_status_sums != 0)
    if len(good_telescopes[0]) > 0:
        return good_telescopes[0][0], good_telescopes[0], bad_telescopes[0]
    else:
        return 4, good_telescopes[0], bad_telescopes[0]


def get_temperature_humidity(pin):
    '''Returns the temperature - see Adafruit for more information.
    It uses adafruits read_retry which will attempt to read the sensor up to
    15 times at 2 second intervals if a value cannot be read'''
    sensor = Adafruit_DHT.DHT11
    print('reading temperature/humidity on pin %r' % pin)
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity, temperature

#defuct function, not used in code but useful for testing
def get_humidity(pin):
    '''Returns the temperature - see Adafruit  to figure out how this works'''
    sensor = Adafruit_DHT.DHT11
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity

def get_button(pin):
    '''Returns a 1 if the button is pressed '''
    print('reading button on pin %r' % pin)
    input_state = GPIO.input(pin)
    if input_state == False:
        return 1
    else:
        return 0

def move_telescope(telescope, posn):
    '''A function for moving the selected telescope from
    one position to another'''
    print('moving telescope %r to %r' % (telescope, posn))
    if telescope <= 3:
        move_servo(pins[telescope, 0], posn[0])
        move_servo(pins[telescope, 1], posn[1])
    else:
        print('activating imaginary telescope')
    return None


def move_servo(pin, degrees):
    #150 = 0 degrees, 600 = 180 degrees
    '''Moves the servo - tested on 180 degree servos.
    The code will stop the servo from moving outside its
    desgned area of travel and breaking itself.'''
    pulse = int(round((degrees*450/180)+150))  
    if pulse < 151:
        pulse = 151
        print ('invalid movement - limiting to 0')
    elif pulse > 599:
        pulse = 599
        print('invalid movement - limiting to 180')
    print('servo on pin %r moving by %r degrees (pulse = %r)' %(pin, degrees, pulse))
    pwm.set_pwm(pin, 0, pulse)


def get_sensors(comparitive_values):
    '''A function for reading the sensor values.
    Returns a 4 * 3 array of binary values and a direct measurement
    of the temperature/humidity. Each row corresponds to
    a telescope and each column a sensor. A value of 1 implies the
    sensor has been triggered.
    The input of compariteve vales is an array of previously measured
    values for comparison. If temperature or humidity have changed by 2
    degrees/percent it will output as triggered.'''
    print('getting sensors')
    binary_arr = np.zeros((4,3))
    new_comparitive_values = np.zeros((4,2))
    i = 0
    while i <= 3:        
        new_comparitive_values[i,:] = get_temperature_humidity(pins[i,3])
        binary_arr[i,0] = get_button(pins[i,2])
        if new_comparitive_values[i,0] - comparitive_values[i,0] > 2:
            binary_arr[i,1] = 1
        if new_comparitive_values[i,1] - comparitive_values[i,1] > 2:
            binary_arr[i,2] = 1
        i +=1
    print(binary_arr)
    print(new_comparitive_values)
    return binary_arr, new_comparitive_values

def turn_on_off_led(pin, on_off):
    if on_off == 1:
        GPIO.output(pin, GPIO.HIGH)
    else:
        GPIO.output(pin, GPIO.LOW)

def update_leds(good_telescopes, bad_telescopes):
    for m in range(len(good_telescopes)):
        turn_on_off_led(pins[good_telescopes[m],5], 1)
        turn_on_off_led(pins[good_telescopes[m],4], 0)
    for n in range(len(bad_telescopes)):
        turn_on_off_led(pins[good_telescopes[n],4], 1)
        turn_on_off_led(pins[good_telescopes[n],5], 0)


if __name__ == "__main__":
    try:
        main_function()
    except KeyboardInterrupt:
        print('Ending Now')
    finally:
        print('Moving all to park')
        move_telescope(0, np.ones(2))
        move_telescope(1, np.ones(2))
        move_telescope(2, np.ones(2))
        move_telescope(3, np.ones(2))
        print('Running GPIO cleanup')
        GPIO.cleanup()
        
