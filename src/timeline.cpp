#include "timeline.h"
#include "entrance.h"
#include "service_station.h"
#include "queue.h"
#include <iostream>

bool TimeLine::initialize()
{
    // Initialize queue if not already initialized
    if (!queue)
    {
        queue = std::make_shared<Queue>();
    }

    if (!queue->initialize())
    {
        return false;
    }

    // Entrances
    for (auto &entrance : this->entrances)
    {
        if (!entrance->initialize())
        {
            return false;
        }
    }

    // Service Stations
    for (auto &station : this->service_stations)
    {
        if (!station->initialize())
        {
            return false;
        }
    }

    return true;
}

bool TimeLine::is_empty() const
{
    return this->events.empty();
}

bool TimeLine::add_entrance(std::shared_ptr<Entrance> e)
{
    e->set_timeline(shared_from_this());
    this->entrances.push_back(e);
    return true;
}

bool TimeLine::add_customer_group(std::shared_ptr<CustomerGroup> g)
{
    if (!g)
    {
        return false;
    }

    this->customer_groups.push_back(g);
    return true;
}

bool TimeLine::add_service_station(std::shared_ptr<ServiceStation> s)
{
    this->service_stations.push_back(s);
    return true;
}

bool TimeLine::add_event(const Time &time, const Function &func)
{
    this->events.emplace(time, func);
    return true;
}

bool TimeLine::run_next_event()
{
    if (this->events.empty())
    {
        return false;
    }

    auto next_event = this->events.top();
    this->events.pop();

    next_event.second();

    return true;
}

bool TimeLine::print_timeline() const
{
    std::priority_queue<Event, std::vector<Event>, EventCompare> temp_events = this->events;

    while (!temp_events.empty())
    {
        auto event = temp_events.top();
        temp_events.pop();
        std::cout << "Event at time: " << event.first.toMinutes() << " minutes\n";
    }
    return true;
}

std::shared_ptr<Entrance> TimeLine::get_entrance() const
{
    if (entrances.empty() || !entrances.front())
    {
        return nullptr;
    }

    return entrances.front();
}