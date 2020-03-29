from __future__ import print_function

from builtins import range
import MalmoPython
import os
import sys
import time
import random
import json
import math

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

# -- set up the mission -- #
missionXML_file='nb4tf4i_d.xml'
with open(missionXML_file, 'r') as f:
    print("NB4tf4i's Red Flowers (Red Flower Hell) - DEAC-Hackers Battle Royale Arena\n")
    print("NB4tf4i vĂśrĂśs pipacsai (VĂśrĂśs Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n\n")
    print("The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    print("Ennek az elsĹ, az nb4tf4i vĂśrĂśs virĂĄgai nevĹą kihĂ­vĂĄsnak a cĂŠlja ĂśsszegyĹąjteni annyi piros virĂĄgot, amennyit csak lehet, mielĹtt a lĂĄva lefolyik a hegyoldalon.\n")    
    print("Norbert BĂĄtfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n\n")    
    print("Loading mission from %s" % missionXML_file)
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission.drawBlock( 0, 0, 0, "lava")


class Hourglass:
    def __init__(self, charSet):
        self.charSet = charSet
        self.index = 0
    def cursor(self):
        self.index=(self.index+1)%len(self.charSet)
        return self.charSet[self.index]

hg = Hourglass('|/-\|')

class Steve:
    def __init__(self, agent_host):
        self.agent_host = agent_host
        self.x = 0
        self.y = 0
        self.z = 0        
        self.yaw = 0
        self.pitch = 0        

    def turn(self):
        self.agent_host.sendCommand("turn 1")

    def move(self):
        self.agent_host.sendCommand("move 1")

    def wait(self):
        time.sleep(1.0)
        
    def run(self):
        world_state = self.agent_host.getWorldState()
        # Loop until mission ends:

        initialTurn = True
        turnCount = 0
        stepCount = 0
        level = 1
        levelRound = 1

        levelIncreaser = 0

        while world_state.is_mission_running:

            if world_state.number_of_observations_since_last_state != 0:
                
                sensations = world_state.observations[-1].text
                print("    sensations: ", sensations)                
                observations = json.loads(sensations)
                nbr3x3x3 = observations.get("nbr3x3", 0)
                print("    3x3x3 neighborhood of Steve: ", nbr3x3x3)
                pickedFlower = False
                if "LineOfSight" in observations:
                    lineOfSight = observations["LineOfSight"]
                    self.lookingat = lineOfSight["type"]
                    print(self.lookingat)
                    
                    if self.lookingat == 'red_flower':
                        self.agent_host.sendCommand("attack 1")
                        self.wait()
                        pickedFlower = True

                if not pickedFlower and nbr3x3x3[13] == 'red_flower':
                    time.sleep(0.35)
                    self.agent_host.sendCommand("look 1")
                    time.sleep(0.05)
                    self.agent_host.sendCommand("attack 1")
                    self.agent_host.sendCommand("look -1")
                    time.sleep(0.05)
                    self.wait()
                    self.agent_host.sendCommand("jumpmove 1")
                    stepCount += 1
                    pickedFlower = True
                    
                if pickedFlower:
                    # Task 1: Print Debug msg
                    print('\nSteve talalt egy piros viragot!\n')
                    time.sleep(0.35)

                if "Yaw" in observations:
                    self.yaw = int(observations["Yaw"])
                if "Pitch" in observations:
                    self.pitch = int(observations["Pitch"])
                if "XPos" in observations:
                    self.x = int(observations["XPos"])
                if "ZPos" in observations:
                    self.z = int(observations["ZPos"])        
                if "YPos" in observations:
                    self.y = int(observations["YPos"])       

                if initialTurn:
                    for i in range(0,4):
                        self.agent_host.sendCommand("move 1")
                    self.turn()
                    initialTurn = False


                if stepCount < 9 + levelIncreaser:
                    self.agent_host.sendCommand("move 1")
                    stepCount += 1
                elif  turnCount == 3:
                    if pickedFlower:
                        self.agent_host.sendCommand("turn 1")
                        self.agent_host.sendCommand("jumpmove 1")
                        self.agent_host.sendCommand("turn -1")
                        self.agent_host.sendCommand("jumpmove 1")
                        self.agent_host.sendCommand("turn -1")
                        self.agent_host.sendCommand("move 1")  
                        self.agent_host.sendCommand("turn 1")
                        stepCount = 1
                    else:
                        self.agent_host.sendCommand("jumpmove 1")   
                        self.agent_host.sendCommand("move 1")   
                        self.agent_host.sendCommand("turn 1")
                        stepCount = 0
                    levelRound = 1
                    level += 1   
                    turnCount = 0
                    levelIncreaser += 4
                else:
                    stepCount = 0
                    self.turn()
                    turnCount += 1

                time.sleep(0.15)

                #print("    Steve's Coords: ", self.x, self.y, self.z)        
                #print("    Steve's Yaw: ", self.yaw)        
                #print("    Steve's Pitch: ", self.pitch)  

            world_state = self.agent_host.getWorldState()

num_repeats = 1
for ii in range(num_repeats):

    my_mission_record = MalmoPython.MissionRecordSpec()

    # Attempt to start a mission:
    max_retries = 6
    for retry in range(max_retries):
        try:
            agent_host.startMission( my_mission, my_mission_record )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                exit(1)
            else:
                print("Attempting to start the mission:")
                time.sleep(2)

    # Loop until mission starts:
    print("   Waiting for the mission to start ")
    world_state = agent_host.getWorldState()

    while not world_state.has_mission_begun:
        print("\r"+hg.cursor(), end="")
        time.sleep(0.15)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:",error.text)

    print("NB4tf4i Red Flower Hell running\n")
    steve = Steve(agent_host)
    steve.run()

print("Mission ended")
# Mission has ended.
