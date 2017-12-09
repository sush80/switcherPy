BOARD = 1
OUT = 1
IN = 1
LOW = 0
HIGH = 1
PUD_DOWN = 1

def setmode(a):
   print("PIN:setmode" + str( a))
def setup(a, b , c = 1):
   print("PIN:setup" + str( a)+ str( b))
def output(a, b):
   print("PIN:output" + str( a)+ str( b))
def cleanup():
   print("PIN:cleanup")
def setwarnings(flag):
   print("PIN:setwarnings" + str( flag))