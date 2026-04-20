#pragma once

#include <queue>
#include <vector>
#include <memory>
#include <utility>

#include "utils.h"

class Entrance;
class ServiceStation;
class CustomerGroup;
class Queue;

class TimeLine : public std::enable_shared_from_this<TimeLine>
{
private:
  using Event = std::pair<Time, Function>;

  struct EventCompare
  {
    bool operator()(const Event &a, const Event &b) const
    {
      return a.first > b.first;
    }
  };

  std::priority_queue<Event, std::vector<Event>, EventCompare> events;
  std::vector<std::shared_ptr<Entrance>> entrances;
  std::vector<std::shared_ptr<CustomerGroup>> customer_groups;
  std::vector<std::shared_ptr<ServiceStation>> service_stations;
  std::shared_ptr<Queue> queue;

public:
  bool initialize();
  bool is_empty() const;
  bool add_entrance(std::shared_ptr<Entrance> e);
  bool add_customer_group(std::shared_ptr<CustomerGroup> g);
  bool add_service_station(std::shared_ptr<ServiceStation> s);
  bool add_event(const Time &time, const Function &func);
  bool run_next_event();
  bool print_timeline() const;
  std::shared_ptr<Entrance> get_entrance() const;

  const std::vector<std::shared_ptr<CustomerGroup>> &get_customer_groups() const
  {
    return customer_groups;
  }

  std::shared_ptr<Queue> getQueue() const
  {
    return queue;
  }

  void setQueue(std::shared_ptr<Queue> q)
  {
    queue = q;
  }
};