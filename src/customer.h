#pragma once

#include "utils.h"
#include <memory>

class TimeLine;

class CustomerGroup : public std::enable_shared_from_this<CustomerGroup>
{
private:
    int customer_id;
    Time arrival_time;
    Time service_time;
    Time queue_time;
    int64_t group_size;
    std::shared_ptr<TimeLine> timeline;

public:
    struct CustomerGroupStats
    {
        int customer_group_id;
        int64_t group_size;
        Time entry_time;
        Time queue_wait_time;
        Time service_start_time;
        Time service_time;
    };
    CustomerGroup();
    CustomerGroup(int id, const Time &arrival);
    ~CustomerGroup() = default;

    int ID() const;
    Time ArrivalTime() const;
    Time ServiceTime() const;
    Time ServiceStartTime() const;
    Time QueueTime() const;

    bool isServed() const;

    bool updateArrivalTime(const Time &current_time);

    bool updateQueueTime(const Time &current_time);

    bool updateServiceTime(const Time &current_time);

    CustomerGroupStats stats() const;

    bool setGroupSize(int64_t size)
    {
        group_size = size;
        return true;
    }

    int64_t getGroupSize() const
    {
        return group_size;
    }

    bool setTimeLine(std::shared_ptr<TimeLine> tl)
    {
        timeline = tl;
        return true;
    }

    std::shared_ptr<TimeLine> getTimeLine() const
    {
        return timeline;
    }

    bool queueToTimeline();
};
