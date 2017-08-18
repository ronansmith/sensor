from __future__ import division
import time
import numpy as np
import Adafruit_DHT
import RPi.GPIO as GPIO
import Adafruit_PCA9685

#all telescope positions used are numpy arrays of the form [altitude, azimuth]
#telescopes 0 to 3 correspond to the real telescopes. Telescope 4 means no telescope is active.
#Currently in test mode: get sensors retrives a random array and move merely prints the move

#Defining the telescope servo and sensor locations
# RA, Dec, button, temp/humid
pins = np.array([11, 12, 18, 23], #telescop 0
                [1, 1, 1, 1], #telescope 1
                [1, 1, 1, 1], #telescope 2
                [1, 1, 1, 1]) #telescope 3
                

#setting up buttons on pins 12 and 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#setting up the pulse width modulation controller for the servos
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)


def find_best_telescope(comparitive_values):
    '''A function for finding the best telescope. The first telescope
    with no triggered sensors is selected. The value returned corresponds
    to this telescope. A value of 4 signifies no telescope without a
    triggered sensor exists'''
    sensor_status, unused_comparitives = get_sensors(comparitive_values)
    if sum(sensor_status[0, :]) < 1:
        return 0
    elif sum(sensor_status[1, :]) < 1:
        return 1
    elif sum(sensor_status[2, :]) < 1:
        return 2
    elif sum(sensor_status[3, :]) < 1:
        return 3
    else:
        return 4
    

def main_function():
    '''The function used to constantly check the sensors and update the telelscope
    accordingly'''

    #defining the park position and a random target to observe
    park = np.zeros(2) 
    telescope_posn = np.array([np.random.randint(30,80), np.random.randint(0,180)])

    current_telescope = 4 #no telescope is currently active
    track_counter = 0 #counter used for tracking
    binary_values, comparitive_values = get_sensors(np.zeros(2,1))

    #infinite loop - consided putting in break??
    while True:
        new_telescope = find_best_telescope(comparitive_values)

        #changing to the new telescope if current telescope is not the best
        if new_telescope != current_telescope:
            move_telescope(current_telescope, park)
            move_telescope(new_telescope, telescope_posn)
            current_telescope = new_telescope

        #tracking - moves the telescope by a degree every 20 seconds
        if track_counter > 20:
            new_posn = telescope_posn[0], telescope_posn[1]+1
            move_telescope(current_telescope, telescope_posn, new_posn)
            telescope_posn = new_posn
            track_counter = 0
        else:
            track_counter +=1
        
        time.sleep(1) #loops the code every 1 seconds
        
    return True

def get_temperature(pin):
    '''Returns the temperature - see Adafruit  to figure out how this works'''
    sensor = Adafruit_DHT.DHT11
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return temperature

def get_humidity(pin):
    '''Returns the temperature - see Adafruit  to figure out how this works'''
    sensor = Adafruit_DHT.DHT11
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity

def get_button(pin):
    '''Returns a 1 if the button is pressed '''
    input_state = GPIO.input(pin)
    if input_state == False:
        return 1
    else:
        return 0

def move_telescope(telescope, posn):
    '''A function for moving the selected telescope from
    one position to another'''
    if telescope <= 3:
        move_servo(pins[telescope, 0], posn[0])
        move_servo(pins[telescope, 1], posn[1])
    else:
        print('activating imaginary telescope')
    return None

def move_servo(pin, degrees):
    #150 = 0 degrees, 600 = 180
    '''Moves the servo '''
    pulse = int(round((degrees*450/180)+150))
    if pulse < 151:
        pulse = 151
        print ('invalid movement')
    elif pulse > 599:
        pulse = 599
        print('invalid movement')
    pwm.set_pwm(pin, 0, pulse)

def get_sensors(comparitive_values):
    '''A function for reading the sensor values.
    Returns a 4 * 3 array of binary values and a direct measurement
    of the temperature/humidity. Each row corresponds to
    a telescope and each column a sensor. A value of 1 implies the
    sensor has been triggered. '''
    binary_arr = np.zeros((3,1))
    new_comparitive_values = np.zeros((2,1))
    i = 0
    for i in range(3):        
        new_comparitive_values[i,0] = get_temperature(pins[i,3])
        new_comparitive_values[i,1] = get_humidity(pins[i,3])
        binary_arr[i,0] = get_button(pins[i,2])
        if new_comparitive_values[i,0] - comparitive_values[i,0] > 2:
            binary_arr[i,1] = 1
        if new_comparitive_values[i,1] - comparitive_values[i,1] > 2:
            binary_arr[i,2] = 1
        i +=1
    return binary_arr, new_comparitive_values


if __name__ == "__main__":
    i = 90
    while True:
        if get_button(12) == 1:
            i +=1
        elif get_button(18) ==  1:
            i -=1
        move_servo(100, i)
        time.sleep(0.5)
        
