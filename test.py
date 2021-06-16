
accept = ["G", "M", "X", "Y", "I", "J", "F"]

G = "G01 X123 Y231 F200"



"""
asd = ["543", "5", "2", "1", "450"]

print(list(map(int, asd))) # Turns a list of strings of numbers asd into ints 
"""


storage = [0, 0, 0, 0, 0, 0, 0]
store_in = 0


digits = 0
for char in G :
    
    print(char)
    if char.isalpha() :
        digits = 0 # Reset, ready for next number
        char = char.upper()
        store_in = accept.index(char) #Put the following number in the right place in storage
        
        if char == "G" or char == "M" :
            sig_figs = 2
        else:
            sig_figs = 3
        
    elif char.isdigit() and digits <= sig_figs:
        char = int(char) # Turn it into an integer
        digits += 1
        storage[store_in] += char * (10 ** (sig_figs - digits))# Store the number, and move it left one decimal place
        
        
        
    print(storage)
