from maestro import Controller

# These are the port values:
#MOTOR_FWD_BKWD = 0...#controls (31005900 stops, Forward max = 3500  9000 top speed(SUPER fast) Stall = 5900)
#MOTORTURN_L_R = 1...6000 is quiet stop 6600 is slow left 7500 is faster 8000 max 5500 ... 3000 is right fast is slow right turn
#WAIST = 2...#controls (Right max = 4000, Mid = 6000, Left Max = 8000)
HEADNOD = 3 #controls (Mid = 5500, Up = 7500, Down = 3500) 
HEADTURN = 4 #controls (4000, 6500, 9000)
#R_SHOULDER = 5 #controls (Up = 10,000)
#R_BICEP = 6
#R_ELBOW = 7
#R_UPPER_FREARM = 8
#R_WRIST = 9
#R_GRIPPER = 10
#L_SHOULDER = 11 #controls (Up = 7,000... Down = 9,000)
#L_BICEP = 12 #controls (Out of body = 5500, Straight = 6500, In body = 7500)
#L_ELBOW = 13 #controls (Backward = 4000, Straight = 6600, Forward = 8000)
#L_UPPER_FREARM = 14 #controls (UP = 4000, Straight 5500, = Backward = 8000)
#L_WRIST = 15 #controls (into body = 3500, straight = 6000, out of body = 8500)
#L_GRIPPER = 16 # controls (close = 7500, open = 3000, middle = 5500)

##text = input("Format: Port#.Value# \nEnter q to quit >> ")
##while(text != "q"):
##    turn = int(text.split(".")[1])
##    port = int(text.split(".")[0])
##    print(port, turn)
##    #self.tango.setTarget(port, self.turn)
##    text = input(">> ")



class Tango:
    def __init__(self):
        self.tango = Controller()
        self.turn = 0
        self.tango.setTarget(HEADTURN, self.turn)
        text = input("Format: Port#.Value# \nEnter q to quit >> ")
        while(text != "q"):
            self.turn = int(text.split(".")[1])
            port = int(text.split(".")[0])
            self.tango.setTarget(port, self.turn)
            text = input(">> ")
        
        

t = Tango()
