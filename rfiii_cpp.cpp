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

// Malmo:

#include <AgentHost.h>
#include <ClientPool.h>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/foreach.hpp>
using namespace malmo;

// STL:
#include <cstdlib>
#include <exception>
#include <iostream>
using namespace std;

vector<string> GetItems(WorldState world_state,std::stringstream & ss, boost::property_tree::ptree & pt)
{
    vector<string> nbr3x3;

    ss.clear();
    pt.clear();

    TimestampedString * sensations = world_state.observations.at(0).get();
    ss << sensations->text;
    boost::property_tree::read_json(ss, pt);
    BOOST_FOREACH(boost::property_tree::ptree::value_type &v, pt.get_child("nbr3x3"))
    {
        assert(v.first.empty());
        nbr3x3.push_back(v.second.data());
    }

    //delete sensations;

    return nbr3x3;
}

int main(int argc, const char **argv)
{
    AgentHost agent_host;

    try
    {
        agent_host.parseArgs(argc, argv);
    }
    catch( const exception& e )
    {
        cout << "ERROR: " << e.what() << endl;
        cout << agent_host.getUsage() << endl;
        return EXIT_SUCCESS;
    }
    if( agent_host.receivedArgument("help") )
    {
        cout << agent_host.getUsage() << endl;
        return EXIT_SUCCESS;
    }

    std::ifstream xmlf("nb4tf4i_d.xml");
    std::string xml {std::istreambuf_iterator<char>(xmlf),std::istreambuf_iterator<char>()};

    MissionSpec my_mission {xml,true};
    /*my_mission.timeLimitInSeconds(10);
    my_mission.requestVideo( 320, 240 );
    my_mission.rewardForReachingPosition(19.5f,0.0f,19.5f,100.0f,1.1f);*/

    MissionRecordSpec my_mission_record("./saved_data.tgz");
    /*my_mission_record.recordCommands();
    my_mission_record.recordMP4(20, 400000);
    my_mission_record.recordRewards();
    my_mission_record.recordObservations();*/

    int attempts = 0;
    bool connected = false;
    do {
        try {
            agent_host.startMission(my_mission, my_mission_record);
            connected = true;
        }
        catch (exception& e) {
            cout << "Error starting mission: " << e.what() << endl;
            attempts += 1;
            if (attempts >= 3)
                return EXIT_FAILURE;    // Give up after three attempts.
            else
                boost::this_thread::sleep(boost::posix_time::milliseconds(1000));   // Wait a second and try again.
        }
    } while (!connected);

    WorldState world_state;

    cout << "Waiting for the mission to start" << flush;
    do {
        cout << "." << flush;
        boost::this_thread::sleep(boost::posix_time::milliseconds(100));
        world_state = agent_host.getWorldState();
        for( boost::shared_ptr<TimestampedString> error : world_state.errors )
            cout << "Error: " << error->text << endl;
    } while (!world_state.has_mission_begun);
    cout << endl;

    world_state = agent_host.getWorldState();

    bool pickedFlower = false;
    bool jumpedY = false;
    bool initialTurn = true;

    double y = 0;
    int levelIncrement = 0;
    double yPos = 0;
    int turnCount = 0;
    double yaw = 0;

    int stepCount = 0;

    agent_host.sendCommand("look 1");
    agent_host.sendCommand("look 1");

    bool rf = false;

    do {

        if(world_state.number_of_observations_since_last_state != 0)
        {
            TimestampedString * sensations = world_state.observations.at(0).get();

            std::stringstream ss;
            ss << sensations->text;
            boost::property_tree::ptree pt;
            boost::property_tree::read_json(ss, pt);

            vector<std::string> nbr3x3;

            nbr3x3 = GetItems(world_state,ss,pt);

            if(yaw == 0 && nbr3x3[11] == "dirt" && nbr3x3[14] == "dirt")
            {
                 agent_host.sendCommand("turn -1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                 agent_host.sendCommand("turn -1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                 agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                 agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                 agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                 agent_host.sendCommand("turn -1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                turnCount -= 1;
                stepCount = ceil(levelIncrement / 2) - 2;
            }


            for(unsigned int i=0;i<nbr3x3.size();i++)
            {
                if(nbr3x3[i] == "red_flower")
                {
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    world_state = agent_host.getWorldState();
                    while(world_state.observations.size() == 0)
                    {
                        world_state = agent_host.getWorldState();
                    }
                    
                    nbr3x3 = GetItems(world_state,ss,pt);
                    rf = true;
                    break;
                }
            }
            pickedFlower = false;

            string los = pt.get<std::string>("LineOfSight.type");

            if(los == "red_flower")
            {
                agent_host.sendCommand("attack 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                pickedFlower = true;
            }

           cout << (nbr3x3[13]) << endl;

            if(!pickedFlower && nbr3x3[13] == "red_flower")
            {
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                agent_host.sendCommand("attack 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));

                world_state = agent_host.getWorldState();

                agent_host.sendCommand("hotbar.2 1");
                agent_host.sendCommand("jumpuse 2");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                pickedFlower = true;
            }

            y = pt.get<double>("YPos");
            yaw = pt.get<double>("Yaw");

            if(y == 3) levelIncrement = (y - 2) * 4;
            else levelIncrement = (y - 3) * 4;

            if(pickedFlower)
            {
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                agent_host.sendCommand("turn -1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                agent_host.sendCommand("turn 1");
                agent_host.sendCommand("move 1");
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));    
                turnCount -= 1;      
                yPos = y;
                stepCount -= 4;
            }

            if(initialTurn)
            {
                agent_host.sendCommand("turn 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                agent_host.sendCommand("turn 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                for(unsigned int i=0;i<5;i++)
                {
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                }
                agent_host.sendCommand("jumpmove 1");
                for(unsigned int i=0;i<28;i++)
                {
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                    agent_host.sendCommand("jumpmove 1");
                }
                for(unsigned int i=0;i<20;i++)
                {
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(50));
                }
                turnCount -= 1;
                agent_host.sendCommand("turn -1");
                initialTurn = false;
                stepCount = ceil(levelIncrement / 2);
            }
            
            if(stepCount < 9 + levelIncrement){}
            else if(turnCount == 3)
            {
                if(pickedFlower)
                {
                    agent_host.sendCommand("turn -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("jumpmove 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("turn -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("turn 1");
                    stepCount = 1;
                }
                else
                {
                    agent_host.sendCommand("turn -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("turn -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                    agent_host.sendCommand("turn 1");
                    stepCount = 0;
                }
                turnCount = 0;
            }
            else
            {
                if(pickedFlower)
                {
                    agent_host.sendCommand("turn -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(85));
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(85));
                    agent_host.sendCommand("turn -1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(85));
                    agent_host.sendCommand("move 1");
                    agent_host.sendCommand("move 1");
                    boost::this_thread::sleep(boost::posix_time::milliseconds(85));
                    agent_host.sendCommand("turn 1");
                }
                stepCount = 0;
                // stepcount
                boost::this_thread::sleep(boost::posix_time::milliseconds(85));
                if(jumpedY == false)
                    agent_host.sendCommand("turn -1");

                turnCount += 1;
            }
        

            jumpedY = false;

            if(yPos == y && pickedFlower == false)
            {
            // boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("turn -1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("turn -1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("move 1");
                boost::this_thread::sleep(boost::posix_time::milliseconds(100));
                agent_host.sendCommand("turn 1");
                yPos = 0;
                turnCount = 0;
                jumpedY = true;
                stepCount = 0;
            }
            //delete sensations;
        }

        if(rf) boost::this_thread::sleep(boost::posix_time::milliseconds(15));
       
        rf = false;
        agent_host.sendCommand("move 1");
        stepCount += 1;
        boost::this_thread::sleep(boost::posix_time::milliseconds(48));
        
        world_state = agent_host.getWorldState();
    } while (world_state.is_mission_running);

    cout << "Mission has stopped." << endl;

    return EXIT_SUCCESS;
}
