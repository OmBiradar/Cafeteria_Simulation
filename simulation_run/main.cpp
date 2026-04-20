#include "entrance.h"
#include "timeline.h"
#include "simulation.h"
#include "service_station.h"
#include <iostream>
#include <memory>

int main()
{

    std::cout << "Welcome to the Cafeteria Simulation!" << std::endl;

    for (int i = 0; i < 5; i++)
    {
        std::shared_ptr<Entrance> entrance = std::make_shared<Entrance>();
        entrance->set_arrival_profile_path("./data/average_day_arrivals.csv");
        entrance->set_group_size_profiles_path("./config/group_size_profiles.yaml");
        entrance->set_group_profile_number(i);
        std::shared_ptr<TimeLine> timeline = std::make_shared<TimeLine>();
        std::shared_ptr<HumanServiceStation>
            human_station = std::make_shared<HumanServiceStation>();

        timeline->add_entrance(entrance);
        timeline->add_service_station(human_station);

        std::shared_ptr<Simulation> sim = std::make_shared<Simulation>(timeline);
        sim->initialize();
        sim->run();
        sim->save_results("./results");
    }

    return 0;
}