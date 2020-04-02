from __future__ import print_function
# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #2: Run simple mission using raw XML

# Added modifications by Norbert BĂĄtfai (nb4tf4i) batfai.norbert@inf.unideb.hu, mine.ly/nb4tf4i.1
# 2018.10.18, https://bhaxor.blog.hu/2018/10/18/malmo_minecraft
# 2020.02.02, NB4tf4i's Red Flowers, http://smartcity.inf.unideb.hu/~norbi/NB4tf4iRedFlowerHell


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
        self.agent_host.sendCommand("turn -1")

    def move(self):
        self.agent_host.sendCommand("move 1")

    def wait(self):
        time.sleep(0.45)

    def getPlaceableBlockIndex(self,obj):
        index = -1
        for key in obj:
            data = key.split('_')
            if data[0] == 'Hotbar' and data[2] == 'item':
                if obj[key] == 'dirt':
                    index = int(data[1])
                    break
        return index+1 # Note: The slots are 0-indexed but the key commands are 1-indexed, so to select slot 8, the command sequence would be 9

        
    def run(self):
        world_state = self.agent_host.getWorldState()
        # Loop until mission ends:

        initialMovement = True

        invertedDirection = False

        self.agent_host.sendCommand("move 1")
        self.agent_host.sendCommand("move 1")
        self.agent_host.sendCommand("move 1")

        while world_state.is_mission_running:

            if world_state.number_of_observations_since_last_state != 0:
                
                sensations = world_state.observations[-1].text                
                observations = json.loads(sensations)
                nbr3x3x3 = observations.get("nbr3x3", 0)     

                minedFlower = False

                if "LineOfSight" in observations:
                    lineOfSight = observations["LineOfSight"]
                    self.lookingat = lineOfSight["type"]
                    #print(self.lookingat)
                    
                    if self.lookingat == 'red_flower':
                        self.agent_host.sendCommand("attack 1")    
                        minedFlower = True

                if not minedFlower and nbr3x3x3[13] == 'red_flower':
                    self.agent_host.sendCommand("look 1")    
                    time.sleep(0.05)
                    self.agent_host.sendCommand("attack 1")    
                    time.sleep(0.05)
                    self.agent_host.sendCommand("jumpmove 1")  
                    time.sleep(0.05)
                    self.agent_host.sendCommand("look -1") 

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

                if 'flowing_lava' in nbr3x3x3 and initialMovement:
                    self.agent_host.sendCommand('turn 1')
                    time.sleep(0.25)

                if 'flowing_lava' in nbr3x3x3:
                    initialMovement = False              

                print(self.yaw)

                if (nbr3x3x3[19] == 'flowing_lava' and self.yaw == 0) or (nbr3x3x3[25] == 'flowing_lava' and self.yaw == 180):
                    self.agent_host.sendCommand('turn 1')
                    self.agent_host.sendCommand('turn 1')
                    self.agent_host.sendCommand('move 1')
                    self.agent_host.sendCommand('move 1')
                    self.agent_host.sendCommand('turn 1')
                    self.agent_host.sendCommand('move 1')
                    self.agent_host.sendCommand('move 1')
                    self.agent_host.sendCommand('turn -1')
                    invertedDirection = not invertedDirection
                    continue

                if 'flowing_lava' in nbr3x3x3:
                    if not invertedDirection:
                        self.agent_host.sendCommand('turn 1')
                        time.sleep(0.25)
                        self.agent_host.sendCommand('move 1')
                        time.sleep(0.25)
                        self.agent_host.sendCommand('turn 1')
                        invertedDirection = not invertedDirection
                    else:
                        self.agent_host.sendCommand('turn -1')
                        time.sleep(0.25)
                        #self.agent_host.sendCommand('move 1')
                        #time.sleep(0.25)
                        self.agent_host.sendCommand('move 1')
                        time.sleep(0.25)
                        self.agent_host.sendCommand('turn -1')
                        invertedDirection = not invertedDirection
                elif initialMovement:
                    self.agent_host.sendCommand("jumpmove 1")
                    time.sleep(0.2)
                else:
                   self.agent_host.sendCommand("move 1")
                   time.sleep(0.35)

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
