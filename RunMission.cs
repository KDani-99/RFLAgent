// --------------------------------------------------------------------------------------------------
//  Copyright (c) 2016 Microsoft Corporation
//  
//  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
//  associated documentation files (the "Software"), to deal in the Software without restriction,
//  including without limitation the rights to use, copy, modify, merge, publish, distribute,
//  sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//  
//  The above copyright notice and this permission notice shall be included in all copies or
//  substantial portions of the Software.
//  
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
//  NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
//  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
//  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
// --------------------------------------------------------------------------------------------------

using System;
using System.Threading;
using Microsoft.Research.Malmo;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;
class Program
{
    public static void Main()
    {
        for(int run=0;run<1;run++)
        {
            Console.WriteLine("Run #" + run);
        
            AgentHost agentHost = new AgentHost();
            try
            {
                agentHost.parse( new StringVector( Environment.GetCommandLineArgs() ) );
            }
            catch( Exception ex )
            {
                Console.Error.WriteLine("ERROR: {0}", ex.Message);
                Console.Error.WriteLine(agentHost.getUsage());
                Environment.Exit(1);
            }
            if( agentHost.receivedArgument("help") )
            {
                Console.Error.WriteLine(agentHost.getUsage());
                Environment.Exit(0);
            }

            bool pretty_print = false;
            string xml = System.IO.File.ReadAllText(System.IO.Directory.GetCurrentDirectory()+"/mission.xml");

            MissionSpec mission = null;
            bool validate = true;
            mission = new MissionSpec(xml, validate);

            Random rand2 = new Random();

            for (int i = 0; i < rand2.Next(5, 15); i++)
                mission.drawBlock(rand2.Next(1, 10), 46, rand2.Next(1, 10), "red_flower");

            MissionRecordSpec missionRecord = new MissionRecordSpec("./saved_data.tgz");
            missionRecord.recordCommands();
            missionRecord.recordMP4(20, 400000);
            missionRecord.recordRewards();
            missionRecord.recordObservations();      

            bool connected = false;
            int attempts = 0;
            while (!connected)
            {
                try
                {
                    attempts += 1;
                    agentHost.startMission(mission, missionRecord);
                    connected = true;
                }
                catch (MissionException ex)
                {
                    // Using catch(Exception ex) would also work, but specifying MissionException allows
                    // us to access the error code:
                    Console.Error.WriteLine("Error starting mission: {0}", ex.Message);
                    Console.Error.WriteLine("Error code: {0}", ex.getMissionErrorCode());
                    // We can do more specific error handling using this code, eg:
                    if (ex.getMissionErrorCode() == MissionException.MissionErrorCode.MISSION_INSUFFICIENT_CLIENTS_AVAILABLE)
                        Console.Error.WriteLine("Have you started a Minecraft client?");
                    if (attempts >= 3)   // Give up after three goes.
                        Environment.Exit(1);
                    Thread.Sleep(1000); // Wait a second and try again.
                }
            }
            WorldState worldState;

            Console.WriteLine("Waiting for the mission to start");
            do
            {
                Console.Write(".");
                Thread.Sleep(100);
                worldState = agentHost.getWorldState();

                foreach (TimestampedString error in worldState.errors) Console.Error.WriteLine("Error: {0}", error.text);
            }
            while (!worldState.has_mission_begun);
        
            Console.WriteLine();

            Random rand = new Random();

            Queue<JToken> apples = new Queue<JToken>();
            bool observed = false;

            // main loop:
            do
            {

                //agentHost.sendCommand(string.Format("turn {0}", rand.NextDouble()));
                Thread.Sleep(500);
                worldState = agentHost.getWorldState();
                //agentHost.sendCommand("pitch 1");
                if (!observed)
                {
                    JObject obj = JObject.Parse(worldState.observations[0].text);

                    JToken entities;

                    if (obj.TryGetValue("close_entities", out entities))
                    {

                        JArray entitiesArr = (JArray)entities;

                        // The first element is always our agent ? - maybe
                        for (int i = 1; i < entitiesArr.Count; i++)
                        {
                            Console.WriteLine(entitiesArr[i]["name"]);
                            if ((string)entitiesArr[i]["name"] == "red_flower")
                                apples.Enqueue(entitiesArr[i]);
                        }

                        observed = true;
                    }
                }
                else
                {
                    // Start trying to get to the apples

                    if(apples.Count == 0)
                    {
                        Console.WriteLine("Mission acomplished.");
                        return;
                    }

                    bool popped = false;
                    while(!popped)
                    {
                        var obs = agentHost.getWorldState().observations;
                        if (obs.Count > 0)
                        {
                            // Get our position
                            JObject obj = JObject.Parse(obs[0].text);

                            JToken entities;

                            if (obj.TryGetValue("close_entities", out entities))
                            {

                                JArray entitiesArr = (JArray)entities;

                                // The first element is always our agent ? - maybe
                                Console.WriteLine(entitiesArr[0]);
                                int x = (int)entitiesArr[0]["x"];
                                int z = (int)entitiesArr[0]["z"];

                                int diffX = (int)apples.Peek()["x"] - x;
                                int diffZ = (int)apples.Peek()["z"] - z;

                                Console.WriteLine(diffX + "-" + diffZ);

                                 if (diffZ > 0)
                                     agentHost.sendCommand("movesouth 1");
                                 else if(diffZ < 0)
                                     agentHost.sendCommand("movenorth 1");
                                 if (diffX > 0)
                                     agentHost.sendCommand("moveeast 1");
                                 else if(diffX < 0)
                                     agentHost.sendCommand("movewest 1");

                                /* Console.WriteLine(entitiesArr[0]);
                                 if (diffZ > 0)
                                 {
                                     if((float)entitiesArr[0]["yaw"] > 180)
                                         agentHost.sendCommand("turn 180");
                                     agentHost.sendCommand("move 1");
                                 }
                                 else if (diffZ < 0)
                                 {
                                     agentHost.sendCommand("turn 0");
                                     agentHost.sendCommand("move 1");
                                 }
                                 if (diffX > 0)
                                 {
                                     agentHost.sendCommand("turn -90");
                                     agentHost.sendCommand("move 1");
                                 }
                                 else if (diffX < 0)
                                 {
                                     agentHost.sendCommand("turn 90");
                                     agentHost.sendCommand("move 1");
                                 }*/

                                if (diffZ == 0 && diffX == 0)
                                {
                                    Console.WriteLine("Dequeuing");
                                    agentHost.sendCommand("move 0");
                                    apples.Dequeue();

                                    // break block
                                    agentHost.sendCommand("pitch 1");
                                    agentHost.sendCommand("attack 1");
                                    agentHost.sendCommand("jump 1");
                                    Thread.Sleep(6000);
                                    break;
                                }
                            }
                        }
                        Thread.Sleep(500);
                      //  agentHost.sendCommand("movenorth 1");
                    }
                }


                Console.WriteLine(
                    "video,observations,rewards received: {0}, {1}, {2}",
                    worldState.number_of_video_frames_since_last_state,
                    worldState.number_of_observations_since_last_state,
                    worldState.number_of_rewards_since_last_state);
                foreach (TimestampedReward reward in worldState.rewards) Console.Error.WriteLine("Summed reward: {0}", reward.getValue());
            
                foreach (TimestampedString error in worldState.errors) Console.Error.WriteLine("Error: {0}", error.text);
            }
            while (worldState.is_mission_running);

            Console.WriteLine("Mission has stopped.");
        }
    }
    public static int CalculateMass()
    {
        // Get the position of the area where the red flower count is the greatest to decrease picking time
        // And reward this decision
        return -1;
    }
    public static int GetDistance(int x1, int z1,int x2,int z2)
    {
        return (int)Math.Sqrt(Math.Pow(x2-x1,2) + Math.Pow((z2 - z1),2));
    }
}
