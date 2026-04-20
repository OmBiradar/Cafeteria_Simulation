#include "entrance.h"
#include "utils.h"
#include "customer.h"
#include "timeline.h"
#include <vector>
#include <string>
#include <utility>
#include <yaml-cpp/yaml.h> // Make sure to link against yaml-cpp

#include <fstream>
#include <iostream>
#include <random>
#include <algorithm>

bool Entrance::initialize()
{

    if (!sample_entry_times())
    {
        return false;
    }

    if (!loadCustomersToTimeline())
    {
        return false;
    }

    return true;
}

bool Entrance::load_arrival_profile()
{
    std::ifstream file(this->arrival_profile_path);

    std::string line;

    std::getline(file, line); // Skip header line

    while (std::getline(file, line))
    {
        if (line.empty())
            continue;

        // Replace the comma with a space.
        // "10:00 - 10:10,1" becomes "10:00 - 10:10 1"
        std::replace(line.begin(), line.end(), ',', ' ');

        std::stringstream ss(line);
        Time start_time, end_time;
        int people_count;

        std::string start_time_str, dummy_dash, end_time_str, number_str;

        // This will now perfectly extract all 4 components every time
        if (!(ss >> start_time_str >> dummy_dash >> end_time_str >> number_str))
        {
            std::cerr << "Error parsing line: " << line << std::endl;
            return false;
        }

        start_time.fromString(start_time_str);
        end_time.fromString(end_time_str);
        people_count = std::stoi(number_str);

        arrival_profile.emplace_back(start_time, end_time, people_count);
    }
    return true;
}

bool Entrance::loadCustomersToTimeline()
{
    if (!timeline)
    {
        return false;
    }

    for (const auto &event : this->events)
    {
        timeline->add_event(event.first, event.second);
    }
    return true;
}

bool Entrance::load_group_size_profiles()
{
    try
    {
        // Load the YAML file
        YAML::Node root = YAML::LoadFile(group_size_profiles_path.string());

        // Clear any existing profiles before loading
        group_size_profiles.clear();

        // Iterate through each top-level key (config_1, config_2, etc.)
        for (YAML::const_iterator it = root.begin(); it != root.end(); ++it)
        {
            YAML::Node config_node = it->second;
            GroupSizeProfile profile;

            // 1. Extract and set Profile Name
            if (config_node["name"])
            {
                profile.setProfileName(config_node["name"].as<std::string>());
            }

            // 2. Extract and set Profile Description
            if (config_node["description"])
            {
                profile.setProfileDescription(config_node["description"].as<std::string>());
            }

            // 3. Extract the Probability Distribution
            if (config_node["probability_distribution"])
            {
                std::vector<std::pair<int, double>> dist_pairs;
                YAML::Node prob_node = config_node["probability_distribution"];

                // The distribution is a sequence (list) of maps
                for (std::size_t i = 0; i < prob_node.size(); ++i)
                {
                    YAML::Node item = prob_node[i];

                    // Each item is a map with a single key-value pair (e.g., 1 : 0.35)
                    for (YAML::const_iterator dist_it = item.begin(); dist_it != item.end(); ++dist_it)
                    {
                        int group_size = dist_it->first.as<int>();
                        double probability = dist_it->second.as<double>();
                        dist_pairs.push_back({group_size, probability});
                    }
                }

                // Load the extracted pairs into the sampler
                profile.setConfig(dist_pairs);
            }

            // Add the fully configured profile to the Entrance class vector
            group_size_profiles.push_back(profile);
        }

        return true;
    }
    catch (const YAML::BadFile &e)
    {
        std::cerr << "Error: Could not open group_size_profiles.yaml. " << e.what() << "\n";
        return false;
    }
    catch (const YAML::Exception &e)
    {
        std::cerr << "YAML Parsing Error: " << e.what() << "\n";
        return false;
    }
}

bool Entrance::sample_entry_times()
{
    // Safety check
    if (arrival_profile.empty() || group_size_profiles.empty())
    {
        std::cerr << "Error: Profiles are not loaded yet.\n";
        return false;
    }

    // Standard random number generator setup for the time fractions
    std::random_device rd;
    std::mt19937 rng(rd());
    std::uniform_real_distribution<double> time_fraction_dist(0.0, 1.0);

    events.clear(); // Clear any existing events
    int next_group_id = 0;

    // Loop through every time slot in the CSV
    for (const auto &[start_time, end_time, expected_count] : arrival_profile)
    {
        if (expected_count <= 0)
            continue;

        // --- STEP 1: Determine the groups ---
        int current_sum = 0;
        std::vector<int> groups_in_slot;

        while (current_sum < expected_count)
        {
            // Sample a group size from the selected YAML profile
            int group_size = group_size_profiles[group_profile_number].sample();
            groups_in_slot.push_back(group_size);
            current_sum += group_size;
        }

        // --- STEP 2: Assign random entry times ---
        // (You may need to change .toSeconds() to match your Time class)
        int slot_duration_sec = end_time.toSeconds() - start_time.toSeconds();

        for (int g_size : groups_in_slot)
        {
            // Get a random number between 0.0 and 1.0
            double random_fraction = time_fraction_dist(rng);

            // Calculate how many seconds into the slot they arrive
            int offset_sec = static_cast<int>(random_fraction * slot_duration_sec);

            // Calculate their exact arrival time
            Time entry_time = start_time;
            entry_time.addSeconds(offset_sec); // (Change this if your method is named differently)

            // Create the Event payload (the Function)
            // Capture the timeline by weak_ptr to avoid circular references
            std::weak_ptr<TimeLine> timeline_weak = std::weak_ptr<TimeLine>(timeline);
            const int group_size = g_size;
            const int group_id = next_group_id++;

            Function spawn_group = [group_size, group_id, entry_time, timeline_weak]()
            {
                auto timeline = timeline_weak.lock();
                if (!timeline)
                {
                    std::cerr << "Timeline reference lost when spawning group\n";
                    return;
                }

                std::cout << "CustomerGroup of " << group_size << " arrived at " << entry_time << "\n";

                auto customer_group = std::make_shared<CustomerGroup>(group_id, entry_time);
                customer_group->setGroupSize(group_size);
                customer_group->setTimeLine(timeline);

                if (!timeline->add_customer_group(customer_group))
                {
                    std::cerr << "Failed to register CustomerGroup " << group_id << " in timeline\n";
                    return;
                }

                if (!customer_group->queueToTimeline())
                {
                    std::cerr << "Failed to enqueue CustomerGroup " << group_id << "\n";
                }
            };

            // Add the event to our master list
            events.emplace_back(entry_time, spawn_group);
        }
    }

    // --- STEP 3: Sort the timeline ---
    // Because we picked random times within blocks, the events are out of order.
    // The TimeLine class will likely need them sorted chronologically.
    std::sort(events.begin(), events.end(), [](const Event &a, const Event &b)
              { return a.first.toSeconds() < b.first.toSeconds(); });

    for (const auto &event : events)
    {
        std::cout << "Scheduled Event: Group of " << event.second.target_type().name() << " at " << event.first << "\n";
    }
    return true;
}