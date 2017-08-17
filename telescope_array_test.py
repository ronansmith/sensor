from __future__ import division
import time
import numpy as np
import Adafruit_DHT

#all telescope positions used are numpy arrays of the form [altitude, azimuth]
#telescopes 0 to 3 correspond to the real telescopes. Telescope 4 means no telescope is active.
#Currently in test mode: get sensors retrives a random array and move merely prints the move

def get_sensors():
    '''A function for reading the sensor values.
    Returns a 4 * 3 array of binary values. Each row corresponds to
    a telescope and each column a sensor. A value of 1 implies the
    sensor has been triggered. '''
    return np.random.rand(4,3)

def find_best_telescope():
    '''A function for finding the best telescope. The first telescope
    with no triggered sensors is selected. The value returned corresponds
    to this telescope. A value of 4 signifies no telescope without a
    triggered sensor exists'''
    sensor_status = get_sensors()
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
    
def move_telescope(telescope, initial_posn, final_posn):
    '''A function for moving the selected telescope from
    one position to another'''
    if telescope <= 3:
        print('telescope ' + str(telescope) + ' moved from ' +
              str(initial_posn) + ' to ' + str(final_posn))
    else:
        print('activating imaginary telescope')
    return None

def main_function():
    '''The function used to constantly check the sensors and update the telelscope
    accordingly'''

    #defining the park position and a random target to observe
    park = np.zeros(2) 
    telescope_posn = np.array([np.random.randint(30,80),np.random.randint(0,360)])

    current_telescope = 4 #no telescope is currently active
    track_counter = 0 #counter used for tracking

    #infinite loop - consided putting in break??
    while True:
        new_telescope = find_best_telescope()

        #changing to the new telescope if current telescope is not the best
        if new_telescope != current_telescope:
            move_telescope(current_telescope, telescope_posn, park)
            move_telescope(new_telescope, park, telescope_posn)
            current_telescope = new_telescope

        #tracking - moves the telescope by a degree every 20 seconds
        if track_counter > 20:
            new_posn = telescope_posn[0], telescope_posn[1]+1
            move_telescope(current_telescope, telescope_posn, new_posn)
            telescope_posn = new_posn
            track_counter = 0
        else:
            track_counter +=1
        
        time.sleep(0.1) #loops the code every 0.1 seconds
    return None

def get_temperature('pin'):
    '''Returns the temperature - see Adafruit  to figure out how this works'''
    sensor = Adafruit_DHT.DHT22
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return temperature
    
    
if __name__ == "__main__":
    get_temperature(23)
        
