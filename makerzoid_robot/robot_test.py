from dotenv import load_dotenv
from libraries.makerzoid_robot.robot_control import Robot 
r = Robot()
r.connect()
r.light1(0)
r.light2(0)
r.disconnect(True)