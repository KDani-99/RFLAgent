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

# Sample to demonstrate use of RewardForCollectingItem mission handler - creates a map with randomly distributed food items, each of which
# gives the agent a certain reward. Agent runs around collecting items, and turns left or right depending on the detected reward.
# Also demonstrates use of ObservationFromNearbyEntities

from builtins import range
import MalmoPython
import random
import os
import random
import sys
import time
import json
import random
import errno
from collections import namedtuple
import malmoutils

malmoutils.fix_print()

agent_host = MalmoPython.AgentHost()
malmoutils.parse_command_line(agent_host)

EntityInfo = namedtuple('EntityInfo', 'x, y, z, name, quantity')

def GetMissionXML(summary, itemDrawingXML):
    ''' Build an XML mission string that uses the RewardForCollectingItem mission handler.'''
    
    return '''<?xml version="1.0" encoding="UTF-8" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>''' + summary + '''</Summary>
        </About>

        <ServerSection>
            <ServerHandlers>
                <FlatWorldGenerator generatorString="3;7,220*1,5*3,2;3;,biome_1" />
                <DrawingDecorator>
                    <DrawCuboid x1="-50" y1="226" z1="-50" x2="50" y2="226" z2="50" type="carpet" colour="RED" face="UP"/>
                    ''' + itemDrawingXML + '''
                    <DrawBlock x="0" y="226" z="0" type="red_flower"/>
                    <DrawBlock x="-3" y="256" z="0" type="red_flower"/>
                </DrawingDecorator>
                <ServerQuitFromTimeUp timeLimitMs="150000"/>
                <ServerQuitWhenAnyAgentFinishes />
            </ServerHandlers>
        </ServerSection>

        <AgentSection mode="Survival">
            <Name>The Hungry Caterpillar</Name>
            <AgentStart>
                <Placement x="0.5" y="227.0" z="0.5"/>
                <Inventory>
                </Inventory>
            </AgentStart>
            <AgentHandlers>
                <VideoProducer>
                    <Width>480</Width>
                    <Height>320</Height>
                </VideoProducer>
                <RewardForCollectingItem>
                    <Item reward="2" type="fish porkchop beef chicken rabbit mutton"/>
                    <Item reward="1" type="potato egg carrot red_flower"/>
                    <Item reward="-1" type="apple melon"/>
                    <Item reward="-2" type="sugar cake cookie pumpkin_pie"/>
                </RewardForCollectingItem>
                <ContinuousMovementCommands turnSpeedDegs="180"/>
                <ObservationFromNearbyEntities>
                    <Range name="close_entities" xrange="2" yrange="2" zrange="2" />
                    <Range name="far_entities" xrange="10" yrange="2" zrange="10" update_frequency="100"/>
                </ObservationFromNearbyEntities>
                <ObservationFromGrid>
                      <Grid name="nbr3x3">
                        <min x="-1" y="-1" z="-1"/>
                        <max x="1" y="1" z="1"/>
                      </Grid>
                  </ObservationFromGrid> 
            </AgentHandlers>
        </AgentSection>

    </Mission>'''
  

missionXML_file='nb4tf4i.xml'
with open(missionXML_file, 'r') as f:
    print("NB4tf4i's Red Flowers (Red Flower Hell) - DEAC-Hackers Battle Royale Arena\n")
    print("NB4tf4i vörös pipacsai (Vörös Pipacs Pokol) - DEAC-Hackers Battle Royale Arena\n\n")
    print("The aim of this first challenge, called nb4tf4i's red flowers, is to collect as many red flowers as possible before the lava flows down the hillside.\n")
    print("Ennek az első, az nb4tf4i vörös virágai nevű kihívásnak a célja összegyűjteni annyi piros virágot, amennyit csak lehet, mielőtt a láva lefolyik a hegyoldalon.\n")    
    print("Norbert Bátfai, batfai.norbert@inf.unideb.hu, https://arato.inf.unideb.hu/batfai.norbert/\n\n")    
    print("Loading mission from %s" % missionXML_file)
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission.drawBlock( 0, 0, 0, "lava")
  
def GetItemDrawingXML():
    ''' Build an XML string that contains 400 randomly positioned bits of food'''
    xml=""
    for item in range(250):
        x = str(random.randint(-50,50))
        z = str(random.randint(-50,50))
        type = random.choice(["sugar", "cake", "cookie", "pumpkin_pie", "fish", "porkchop", "beef", "chicken", "rabbit", "mutton", "potato", "egg", "carrot", "apple", "melon"])
        xml += '''<DrawBlock x="''' + x + '''" y="226" z="''' + z + '''" type="''' + "red_flower" + '''"/>'''
    return xml

def SetVelocity(vel): 
    agent_host.sendCommand( "move " + str(vel) )

def SetTurn(turn):
    agent_host.sendCommand( "turn " + str(turn) )

validate = True
# Create a pool of Minecraft Mod clients.
# By default, mods will choose consecutive mission control ports, starting at 10000,
# so running four mods locally should produce the following pool by default (assuming nothing else
# is using these ports):
my_client_pool = MalmoPython.ClientPool()
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10001))
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10002))
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10003))

recordingsDirectory = malmoutils.get_recordings_directory(agent_host)

itemdrawingxml = GetItemDrawingXML()

if agent_host.receivedArgument("test"):
    num_reps = 1
else:
    num_reps = 1

for iRepeat in range(num_reps):
    #my_mission = MalmoPython.MissionSpec(GetMissionXML("Nom nom nom run #" + str(iRepeat), itemdrawingxml),validate)
    # Set up a recording
    my_mission_record = malmoutils.get_default_recording_object(agent_host, "Mission_" + str(iRepeat + 1)) 

    my_mission_record.recordRewards()
    my_mission_record.recordObservations()
    my_mission_record.recordCommands()
    my_mission_record.recordMP4(24,2000000)
    my_mission_record.setDestination(os.getcwd() + "//" + "Mission_" + str(iRepeat + 1) + ".tgz")

    max_retries = 3
    for retry in range(max_retries):
        try:
            # Attempt to start the mission:
            agent_host.startMission( my_mission, my_client_pool, my_mission_record, 0, "itemTestExperiment" )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission",e)
                print("Is the game running?")
                exit(1)
            else:
                time.sleep(2)

    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        time.sleep(0.1)
        world_state = agent_host.getWorldState()

    reward = 0.0    # keep track of reward for this mission.
    turncount = 0   # for counting turn time.
    # start running:
    SetVelocity(1)

    # main loop:
    while world_state.is_mission_running:
        world_state = agent_host.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
           # print(ob)
            if "close_entities" in ob:
                entities = [EntityInfo(k["x"], k["y"], k["z"], k["name"], k.get("quantity")) for k in ob["close_entities"]]
                for ent in entities: pass
                   # print(ent.name, ent.x, ent.z, ent.quantity)
            
            if "far_entities" in ob:
                far_entities = [EntityInfo(k["x"], k["y"], k["z"], k["name"], k.get("quantity")) for k in ob["far_entities"]]
                for ent in far_entities: pass
                  #  print(ent.name, ent.quantity)
            # -------------------------------------------------
            agent_host.sendCommand("move 0.5")
            if "nbr3x3" in ob:
                # Move towards a flower
                # Get agent's facing direction
                itemList = [block for block in ob["nbr3x3"]]

                flowerIndex = -1
                try:
                    flowerIndex = itemList.index('red_flower')
                except ValueError:
                    flowerIndex = -1

                # use loop to determine position for each arr
                south = [0,1,2,9,10,11,18,19,20]
                west = [0,3,6,9,12,15,18,21,24]
                north = [6,7,8,15,16,17,24,25,26]
                east = [2,5,8,11,14,17,20,23,27]

                flowerPos = [x for x in range(0,len(itemList)) if itemList[x] == 'red_flower']
                print(itemList)
                def breakBlock():
                    agent_host.sendCommand("move 0")
                    agent_host.sendCommand("pitch 1")
                    time.sleep(0.5)
                    agent_host.sendCommand("attack 1")
                    time.sleep(1)
                    agent_host.sendCommand("attack 0")
                    agent_host.sendCommand("pitch -1")
                    time.sleep(0.35)
                    agent_host.sendCommand("pitch 0")
                    #jump out of the hole that we've made
                   # agent_host.sendCommand("jump 1")
                    #agent_host.sendCommand("move 1")
                    time.sleep(0.5)
                    #agent_host.sendCommand("jump 0")
                   # agent_host.sendCommand("move 0")

                # if it is greater
                if len(flowerPos) > 0:
                    
                    currentFlower = flowerPos[0]
                    
                    if currentFlower == 4 or currentFlower == 13:
                        breakBlock()
                    elif currentFlower in south:
                        agent_host.sendCommand("turn 90")
                        time.sleep(1)
                        agent_host.sendCommand("move 0.5")
                        time.sleep(0.5)
                        agent_host.sendCommand("move 0")
                        #opposite direction due to turning around
                        if currentFlower in west:
                            agent_host.sendCommand("turn 90")
                            time.sleep(0.5)
                            agent_host.sendCommand("turn 0")
                            agent_host.sendCommand("move 0.5")
                            time.sleep(0.5)
                        elif currentFlower in east:
                            agent_host.sendCommand("turn -90")
                            time.sleep(0.5)
                            agent_host.sendCommand("turn 0")
                            agent_host.sendCommand("move 0.5")
                            time.sleep(0.5)
                        breakBlock()
                    elif currentFlower in north:
                        agent_host.sendCommand("move 0.5")
                        time.sleep(0.5)
                        agent_host.sendCommand("move 0")
                        if currentFlower in west:
                            agent_host.sendCommand("turn 90")
                            time.sleep(0.5)
                            agent_host.sendCommand("turn 0")
                            agent_host.sendCommand("move 0.5")
                            time.sleep(0.5)
                        elif currentFlower in east:
                            agent_host.sendCommand("turn -90")
                            time.sleep(0.5)
                            agent_host.sendCommand("turn 0")
                            agent_host.sendCommand("move 0.5")
                            time.sleep(0.5)
                        breakBlock()
                else:
                    action = random.randint(0,10)
                    if action <= 1:
                        agent_host.sendCommand("turn 0.5")
                    elif action <= 3:
                        agent_host.sendCommand("jump 1")
                    else:
                        agent_host.sendCommand("tmove 0")
                    time.sleep(0.5)
                    agent_host.sendCommand("turn 0")
                    agent_host.sendCommand("move 0")
                    agent_host.sendCommand("jump 0")

        if world_state.number_of_rewards_since_last_state > 0:
            delta = world_state.rewards[0].getValue() 
            if delta != 0:
                agent_host.sendCommand("jump 1")
                agent_host.sendCommand("move 1")
                time.sleep(0.5)
                agent_host.sendCommand("jump 0")
                agent_host.sendCommand("move 0")
        '''
        if world_state.number_of_rewards_since_last_state > 0:
            
            # stop breaking the block
            #agent_host.sendCommand("attack 0")
            #agent_host.sendCommand("jump 1")
            #agent_host.sendCommand("move 1")
            #time.sleep(0.5)
            #agent_host.sendCommand("move 0")
            #agent_host.sendCommand("pitch 0")
            #agent_host.sendCommand("jump 0")


            # A reward signal has come in - see what it is:
            delta = world_state.rewards[0].getValue() 
            if delta != 0:
                # The total reward has changed - use this to determine our turn.
                reward += delta
                turncount = delta
                if turncount < 0:   # Turn left
                    turncount = 1-turncount
                    SetTurn(-1)     # Start turning
                else:               # Turn right
                    turncount = 1+turncount
                    SetTurn(1)      # Start turning
        if turncount > 0:
            turncount -= 1  # Decrement the turn count
            if turncount == 0:
                SetTurn(0)  # Stop turning
        time.sleep(0.1)
        '''
    # mission has ended.
    print("Mission " + str(iRepeat+1) + ": Reward = " + str(reward))
    for error in world_state.errors:
        print("Error:",error.text)
    time.sleep(0.5) # Give the mod a little time to prepare for the next mission.
