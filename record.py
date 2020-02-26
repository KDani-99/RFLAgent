from __future__ import print_function
from lxml import etree
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
missionXML_file='nb4tf4i2.xml'

missionFile = None

with open(missionXML_file, 'r') as f:
    print("NB4tf4i's Red Flowers (Red Flower Hell) - DEAC-Hackers Battle Royale Arena\n")
    print("NB4tf4i vĂśrĂśs pipacsai (VĂśrĂśs Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n\n")
    print("The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    print("Ennek az elsĹ, az nb4tf4i vĂśrĂśs virĂĄgai nevĹą kihĂ­vĂĄsnak a cĂŠlja ĂśsszegyĹąjteni annyi piros virĂĄgot, amennyit csak lehet, mielĹtt a lĂĄva lefolyik a hegyoldalon.\n")    
    print("Norbert BĂĄtfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n\n")    
    print("Loading mission from %s" % missionXML_file)
    mission_xml = f.read()
    missionFile = f.read()
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
        self.nof_red_flower = 0

    def getFlowerPos(self):
        tags = etree.parse('nb4tf4i2.xml')
        root = tags.getroot()

        namespaces = {'None':'http://ProjectMalmo.microsoft.com'}

        flowers = []

        placedBlocks = root.findall('None:ServerSection/None:ServerHandlers/None:DrawingDecorator/None:DrawBlock',namespaces) # hardcoded :*(
        for block in placedBlocks:
            btype = block.get('type')

            if btype == 'red_flower':
                flowerData = {
                    'x':block.get('x'),
                    'y':block.get('y'),
                    'z':block.get('z')
                }
                flowers.append(flowerData)

        flowers.reverse()
        #flowers.pop(0) # first is deadly
            
        return flowers

    def getFlower(self,pos,world_state,isSecond = False):

        pos['x'] = float(pos['x']) + 0.575
        pos['z'] = float(pos['z']) + 0.575

        if isSecond:
            pos['x'] = float(pos['x']) - 0.15
            pos['z'] = float(pos['z']) - 0.15

        self.agent_host.sendCommand('tp '+str(pos['x'])+' '+str(pos['y'])+' '+str(pos['z']))

        time.sleep(0.1)
        self.agent_host.sendCommand('attack 1')
        self.pickedFlower(world_state) # hold thread
    
    def pickedFlower(self,world_state):
        elapsedTime = 0.0
        while world_state.is_mission_running:
            world_state = agent_host.getWorldState()
            if world_state.number_of_rewards_since_last_state > 0:
                delta = world_state.rewards[0].getValue() 
                if delta > 0:
                    break
            elapsedTime += 0.05
            time.sleep(0.05)
            if elapsedTime > 3.0: # move to the next flower (error)
                self.agent_host.sendCommand('move 1')
                time.sleep(0.1)
                self.agent_host.sendCommand('move -1')
                time.sleep(0.1)
                self.agent_host.sendCommand('move 0')
                break

    def run(self):
        world_state = self.agent_host.getWorldState()
        self.getFlowerPos()
        # Loop until mission ends:
        self.agent_host.sendCommand('pitch 1')
        time.sleep(0.35)

        while world_state.is_mission_running:
            flowers = self.getFlowerPos()
            pos = 0
            for flower in flowers:
                self.getFlower(flower,world_state,pos == 1) # contains x,y,z coordinate
                time.sleep(.01)
                pos+=1

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
    print("Number of flowers: "+ str(steve.nof_red_flower))

print("Mission ended")
# Mission has ended.
