#pragma once

#include "utils.h"
#include "customer.h"
#include "timeline.h"
#include "sampler.h"
#include "simulation.h"
#include <filesystem>
#include <memory>
#include <vector>

namespace fs = std::filesystem;

class GroupSizeProfile
{
private:
  WeightedSampler<int> profile_sampler;
  std::string profile_name;
  std::string profile_description;

public:
  GroupSizeProfile() = default;
  ~GroupSizeProfile() = default;
  bool setConfig(const std::vector<std::pair<int, double>> &group_size_prob_pairs)
  {
    return profile_sampler.add_items(group_size_prob_pairs);
  }
  bool setProfileName(const std::string &name)
  {
    profile_name = name;
    return true;
  }
  bool setProfileDescription(const std::string &description)
  {
    profile_description = description;
    return true;
  }
  int sample() const { return profile_sampler.sample(); }
};

class Entrance
{
private:
  using Event = std::pair<Time, Function>;
  std::vector<Event> events;

  fs::path arrival_profile_path;
  std::vector<std::tuple<Time, Time, int>> arrival_profile;

  fs::path group_size_profiles_path;
  std::vector<GroupSizeProfile> group_size_profiles;
  int64_t group_profile_number = 0;

  bool loadCustomersToTimeline();

  bool sample_entry_times();

public:
  Entrance() = default;
  bool set_arrival_profile_path(const fs::path &path)
  {
    arrival_profile_path = path;
    load_arrival_profile();
    return true;
  }
  bool set_group_size_profiles_path(const fs::path &path)
  {
    group_size_profiles_path = path;
    load_group_size_profiles();
    return true;
  }
  bool set_group_profile_number(int64_t number)
  {
    // Check if it's negative, or if it exceeds the bounds of the vector
    if (number < 0 || static_cast<size_t>(number) >= group_size_profiles.size())
    {
      return false;
    }
    group_profile_number = number;
    return true;
  }
  ~Entrance() = default;

  bool load_arrival_profile();
  bool load_group_size_profiles();

  bool initialize(const Simulation::environment &env);
  int64_t get_group_profile_number() const
  {
    return group_profile_number;
  }
};