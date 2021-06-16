# Plotter simulation
# Turns cartesian instructions into angles
# Cameron McDrury 2020

'''
Only two arms this time, but if any more were required it would be best to redesign
so that the program is more robust. Calculations are repeatable for new arms. 
'''


# http://www.deltatau.com/Common/technotes/SCARA%20Robot%20Kinematics.pdf
import os
import sys

import serial
import time
import math

# Define parameters
L1 = 5 # Length of first arm
L2 = 5 # Length of second arm

MaxAngle = 180
MinAngle = 0

# Text prompts:
port_specifier_prompt = "Enter port specifier (eg. COM3) : "
baudrate_prompt = "Enter baud rate (eg. 115200) : "


#Other text:
Accept = ["G", "M", "X", "Y", "I", "J", "F"] # Used chars
Default_feedrate = 200
Rapid_feedrate = 999
Default_codes = [1, 1, 0, 0, 0, 0, -1]

Tool_On = 90
Tool_Off = 0

Current_angles = []
Current_pos = []

time_out = .1

Physical_parameters = [L1, L2, MaxAngle, MinAngle]

angles = [[57.66, 78.46]]

cartesian = []

#[[2, 4], [2, 5], [2, 6], [3, 4], [9, 3]]



    
def read_file(file_path):
    '''Reads a G-code file into an array of target coordinates'''
    
    g_file = open(file_path, "r")
    
    # Turn text into instructions
    
    
    """Go through each line, check for characters representing codes, 
    then read the numbers after them until a space. 
    Use helper functions to interpolate these and make lists of coordinates. 
    Send this list to the arduino. 
    Go to the next line. 
    """
    for line in g_file:
        codes = read_line(line)
        print(codes)
        send_to_arduino(codes)
        
    g_file.close()
    
    
def read_line(line) :
    '''Reads a line of alphanumeric G-Code and returns a list of numbers'''
    
 
    codes = Default_codes
    
    store_in = 0
    digits = 0
    
    for char in line :
        if char.isalpha():
            digits = 0 # Reset, ready for next number
            char = char. upper()
            store_index = Accept.index(char) #Put the following number in the right place in storage
            
            if char == "G" or char == "M":
                sig_figs = 2
            else:
                sig_figs = 3
                
        elif char.isdigit() and digits <= sig_figs:
            char = int(char) # Turn it into an integer
            digits += 1
            codes[store_index] += char * (10 ** (sig_figs - digits)) # Store the number, and move it left one decimal place

    return codes


def send_to_arduino(codes) :
    
    # Get feedrate
    feedrate = codes[Accept.index("F")]
    if feedrate == -1:
        feedrate = Default_feedrate
    
    # Check 'G' codes
    if codes[Accept.index("G")] == 0 : # RAPID MOVE
        angles = linear_interpolation([codes[Accept.index("X")], codes[Accept.index("Y")]], Rapid_feedrate)
        
    elif codes[Accept.index("G")] == 1 : # LINEAR INTERPOLATION
        angles = linear_interpolation([codes[Accept.index("X")], codes[Accept.index("Y")]], codes[Accept.index("F")])
    
    elif codes[Accept.index("G")] == 2 : # CW INTERPOLATION
        angles = circular_interpolation(0, [codes[Accept.index("X")], codes[Accept.index("Y")]], [codes[Accept.index("I")], codes[Accept.index("J")]], codes[Accept.index("F")])
    
    elif codes[Accept.index("G")] == 3 : # CCW INTERPOLATION
        angles = circular_interpolation(1, [codes[Accept.index("X")], codes[Accept.index("Y")]], [codes[Accept.index("I")], codes[Accept.index("J")]], codes[Accept.index("F")])
        
    
    # Check 'M' codes
    if codes[Accept.index("M")] == 0 or codes[Accept.index("M")] == 1 or codes[Accept.index("M")] == 2 : # END OF PROGRAM
        pass
    elif codes[Accept.index("M")] == 3 : # TOOL ON
        angles = [[0, 0, Tool_On]]
    elif codes[Accept.index("M")] == 5 : # TOOL OFF
        angles = [[0, 0, Tool_Off]]
    
    angles = inverse_kinematics(Physical_parameters, cartesian)
    print("Inverse Kinematics: ", angles)

    for angle in angles:
	    print(angle)
	    arduino.write(angle)
        #time.sleep(Feedrate)

def linear_interpolation(destination, feedrate) :
    '''returns a list of coordinates to move to in order to move from
    one place to another through a straight line'''
    
    y_shift = destination[1] - Current_pos[1]
    x_shift = destination[0] - Current_pos[0]
    gradient =  y_shift / x_shift 
    
    n_points = (Rapid_feedrate - feedrate + 1)
    
    x_old = x_shift / n_points
    y_old = y_shift / n_points
    
    points = [[x_old, y_old]]
    
    for i in n_points :
        x_new = x_old * gradient + Current_pos[0]
        y_new = y_old * gradient + Current_pos[1]
        
        points.append([x_new, y_new])
    
    print(points)
    return cartesian_to_radial(points)
    
def circular_interpolation(rotation, destination, centre, feedrate) :
    '''returns a list of coordinates to move to in order to move from
    one place to another through an arc'''
    pass
    
def radial_to_cartesian(angles) :
    ''' Turns angle data into x and y data'''
    
    L1 = params[0]
    L2 = params[1]
    
    cartesian = []
    
    
    for angle_set in angles :
        S = math.radians(angle_set[0])
        E = math.radians(angle_set[1])
        
        X = L1*math.cos(S) + L2*math.cos(S + E)
        Y = L1*math.sin(S) + L2*math.sin(S + E)
        
        cartesian.append([X, Y])

        
    return cartesian

def cartesian_to_radial(cartesian) :
    ''' Turns x and y data into angle data. This one is harder'''
    '''
    for i in cartesian :
        for ii in i :
            print(ii)
    '''
    L1 = Physical_parameters[0]
    L2 = Physical_parameters[1]
    
    angles = []

    
    for point in cartesian :
        theta = 0
        alpha = 0
        '''
        theta = (math.atan(point[1] / point[0]) + math.pi) / ( (1 + L1/L2) * (1 + (math.sqrt(point[0]*point[0] + point[1]*point[1]) / (L2 + L1 )))) 
        alpha = (theta * math.sqrt(point[0]*point[0] + point[1]*point[1])  ) / L2
        '''
        L3 = math.sqrt(point[0]*point[0] + point[1]*point[1])
        
        phi = math.atan(point[1]/ point[0])
        alpha = 2*math.acos(L3/(2*L1))
        theta = math.asin(L1*math.sin(alpha)/L3) + phi
        
        theta = math.degrees(theta)
        alpha = math.degrees(alpha)
        
    
        angles.append([theta, alpha])        
    return angles

def inverse_kinematics(Physical_parameters, cartesian) :
    '''Turns x and y data into angle data. This one is harder'''
    L1 = Physical_parameters[0]
    L2 = Physical_parameters[1]
    
    angles = []
    

    
    for point in cartesian :
        X = point[0]
        Y = point[1]
        
        E = math.acos( (X*X + Y*Y - L1*L1 - L2*L2) / (2*L1*L2) )
        
        Q = math.acos( (X*X + Y*Y + L1*L1 - L2*L2) / (2*L1*math.sqrt(X*X + Y*Y)) )
        
        S = math.atan2(Y, X) - Q
        
        
        angle_set = [round(math.degrees(S) % 180), round(math.degrees(E) % 180)]
        
        #angle_set = check_angles(angle_set)
    
        angles.append(angle_set)      
        
    return angles

def get_port_info() :
    '''Returns the port connected to the arduino, and connects to it'''
    
    # Get port specifier
    # Not very robust, but quick
    
    port = input(port_specifier_prompt)
    
    # Get baud rate
    
    baud_rate = input(baudrate_prompt)
    
    return serial.Serial(port, baud_rate, timeout = time_out)
    


def main(angles, cartesian) :
    ''' Looks after everything'''
    
    #welcome()
    
    arduino = get_port_info()
    
    file_path = input("Please provide the file path to G-Code file (D:\Documents\Passion Projects\Plotter Machine\TEST GCODE.txt): ")
    read_file(file_path)
    
    print("Target: ", cartesian)
    """
    angles = inverse_kinematics(Physical_parameters, cartesian)
    print("Inverse Kinematics: ", angles)

    for angle in angles:
	    print(angle)
	    arduino.write(angle)
"""
    
    while True:
	    data = arduino.readline()[:-2]
	    if data:
	        print(data)       
	             
    angles = cartesian_to_radial(cartesian)
    print("Result (Inverse Kinematics): ", cartesian)
    print("Homebrew: ", angles)
    cartesian = radial_to_cartesian(angles)
    print("Result (Homebrew): ", cartesian)
    
main(angles, cartesian)
