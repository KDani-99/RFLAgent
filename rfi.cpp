#include <AgentHost.h>
#include <ClientPool.h>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/foreach.hpp>
using namespace malmo;

#include <cstdlib>
#include <exception>
#include <iostream>
using namespace std;

vector<string> GetItems(WorldState world_state,std::stringstream & ss, boost::property_tree::ptree & pt)
{
    vector<string> nbr3x3;

    ss.clear();
    pt.clear();

    ss << world_state.observations.at(0).get()->text;
    boost::property_tree::read_json(ss, pt);
    BOOST_FOREACH(boost::property_tree::ptree::value_type &v, pt.get_child("nbr3x3"))
    {
        assert(v.first.empty());
        nbr3x3.push_back(v.second.data());
    }

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

   /* std::ifstream xmlf("nb4tf4i_d.xml");
    std::string xml {std::istreambuf_iterator<char>(xmlf),std::istreambuf_iterator<char>()};*/

    MissionSpec my_mission;
    my_mission.timeLimitInSeconds(10);
    my_mission.startAt(18.5,227.5,642);
    //my_mission.requestVideo( 320, 240 );
    //my_mission.rewardForReachingPosition(19.5f,0.0f,19.5f,100.0f,1.1f);

    MissionRecordSpec my_mission_record("./saved_data.tgz");

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

    do {
        agent_host.sendCommand("move 1");
        boost::this_thread::sleep(boost::posix_time::milliseconds(500));
        ostringstream oss;
        oss << "turn " << rand() / float(RAND_MAX);
        agent_host.sendCommand(oss.str());
        boost::this_thread::sleep(boost::posix_time::milliseconds(500));
        
        world_state = agent_host.getWorldState();
    } while (world_state.is_mission_running);

    cout << "Mission has stopped." << endl;

    return EXIT_SUCCESS;
}
