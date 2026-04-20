#include "simulation.h"

#include <filesystem>
#include <fstream>
#include <map>
#include <sstream>

#include "customer.h"
#include "entrance.h"

namespace
{
    Time time_from_seconds(int total_seconds)
    {
        constexpr int kSecondsPerDay = 24 * 60 * 60;
        int normalized = total_seconds % kSecondsPerDay;
        if (normalized < 0)
        {
            normalized += kSecondsPerDay;
        }

        Time t;
        t.addSeconds(normalized);
        return t;
    }
}

void Simulation::initialize()
{
    env.entrance->initialize(env);
    env.queue->initialize(env);
    env.timeline->initialize(env);
    env.service_station->initialize(env);
}

bool Simulation::run()
{
    if (!timeline)
    {
        return false;
    }

    while (!timeline->is_empty())
    {
        if (!timeline->run_next_event())
        {
            return false;
        }
    }

    return true;
}

bool Simulation::save_results(const std::string &results_directory) const
{
    if (!timeline)
    {
        return false;
    }

    const auto entrance = timeline->get_entrance();
    if (!entrance)
    {
        return false;
    }

    const int64_t profile_index = entrance->get_group_profile_number();

    const auto &customer_groups = timeline->get_customer_groups();

    std::filesystem::path out_dir(results_directory);
    {
        std::error_code ec;
        std::filesystem::create_directories(out_dir, ec);
        if (ec)
        {
            return false;
        }
    }

    const std::filesystem::path customer_data_path = out_dir / ("customer_data_entry_profile_" + std::to_string(profile_index) + ".csv");
    const std::filesystem::path footprint_path = out_dir / ("footprint_profile_" + std::to_string(profile_index) + ".csv");

    std::ofstream out_file(customer_data_path);
    if (!out_file.is_open())
    {
        return false;
    }

    struct FootprintTotals
    {
        int64_t total_customer_groups = 0;
        int64_t total_customers = 0;
    };
    std::map<int, FootprintTotals> footprint_by_slot;

    out_file << "customer_group_id,group_size,entry_time,queue_wait_time,service_start_time,service_time\n";

    for (const auto &group : customer_groups)
    {
        if (!group)
        {
            continue;
        }

        const auto stats = group->stats();

        const int slot_start_seconds = (stats.entry_time.toSeconds() / 600) * 600;
        auto &slot_totals = footprint_by_slot[slot_start_seconds];
        slot_totals.total_customer_groups += 1;
        slot_totals.total_customers += stats.group_size;

        out_file << stats.customer_group_id << ","
                 << stats.group_size << ","
                 << stats.entry_time << ","
                 << stats.queue_wait_time << ","
                 << stats.service_start_time << ","
                 << stats.service_time << "\n";
    }

    if (!out_file.good())
    {
        return false;
    }

    std::ofstream footprint_file(footprint_path);
    if (!footprint_file.is_open())
    {
        return false;
    }

    footprint_file << "time_slot,total_customer_groups,total_customers\n";
    for (const auto &[slot_start_seconds, totals] : footprint_by_slot)
    {
        const Time slot_start = time_from_seconds(slot_start_seconds);
        const Time slot_end = time_from_seconds(slot_start_seconds + 600);

        footprint_file << slot_start << " - " << slot_end << ","
                       << totals.total_customer_groups << ","
                       << totals.total_customers << "\n";
    }

    return footprint_file.good();
}

void Simulation::addTimeline(const std::shared_ptr<TimeLine> &tl)
{
    this->env.timeline = tl;
}

void Simulation::addEntrance(const std::shared_ptr<Entrance> &e)
{
    this->env.entrance = e;
}

void Simulation::addQueue(const std::shared_ptr<Queue> &q)
{
    this->env.queue = q;
}

void Simulation::addServiceStation(const std::shared_ptr<ServiceStation> &s)
{
    this->env.service_station = s;
}
