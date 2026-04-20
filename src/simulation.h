#pragma once

#include <memory>
#include <string>

#include "timeline.h"

class Simulation
{
private:
public:
    struct environment
    {
        std::shared_ptr<TimeLine> timeline;
        std::shared_ptr<Entrance> entrance;
        std::shared_ptr<Queue> queue;
        std::shared_ptr<ServiceStation> service_station;
    } env;

    Simulation() = default;
    ~Simulation() = default;

    void addTimeline(const std::shared_ptr<TimeLine> &tl);
    void addEntrance(const std::shared_ptr<Entrance> &e);
    void addQueue(const std::shared_ptr<Queue> &q);
    void addServiceStation(const std::shared_ptr<ServiceStation> &s);

    void initialize();
    void run();
    void save_results(const std::string &results_directory) const;
};