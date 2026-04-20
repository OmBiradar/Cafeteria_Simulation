#include "customer.h"
#include "timeline.h"
#include "queue.h"

namespace
{
    Time seconds_to_time_non_negative(int total_seconds)
    {
        if (total_seconds < 0)
        {
            total_seconds = 0;
        }

        Time result;
        result.addSeconds(total_seconds);
        return result;
    }
}

CustomerGroup::CustomerGroup() : customer_id(0), arrival_time(), service_time(), queue_time(), group_size(0), timeline(nullptr) {}

CustomerGroup::CustomerGroup(int id, const Time &arrival) : customer_id(id), arrival_time(arrival), service_time(), queue_time(), group_size(0), timeline(nullptr) {}

int CustomerGroup::ID() const
{
    return customer_id;
}

Time CustomerGroup::ArrivalTime() const
{
    return arrival_time;
}

Time CustomerGroup::ServiceTime() const
{
    return service_time;
}

Time CustomerGroup::ServiceStartTime() const
{
    return service_time;
}

Time CustomerGroup::QueueTime() const
{
    return queue_time;
}

bool CustomerGroup::isServed() const
{
    return service_time.getSeconds() > 0 || service_time.getMinutes() > 0 || service_time.getHours() > 0;
}

bool CustomerGroup::updateArrivalTime(const Time &current_time)
{
    arrival_time = current_time;
    return true;
}

bool CustomerGroup::updateQueueTime(const Time &current_time)
{
    queue_time = current_time;
    return true;
}

bool CustomerGroup::updateServiceTime(const Time &current_time)
{
    service_time = current_time;
    return true;
}

CustomerGroup::CustomerGroupStats CustomerGroup::stats() const
{
    const Time service_start_time = ServiceStartTime();
    const Time queue_wait_time = seconds_to_time_non_negative(service_start_time.toSeconds() - arrival_time.toSeconds());
    const Time service_duration;

    return CustomerGroupStats{
        customer_id,
        group_size,
        arrival_time,
        queue_wait_time,
        service_start_time,
        service_duration};
}

bool CustomerGroup::queueToTimeline()
{
    if (!timeline)
    {
        return false;
    }

    auto queue = timeline->getQueue();
    if (!queue)
    {
        return false;
    }

    updateQueueTime(arrival_time);

    return queue->addCustomerGroup(shared_from_this());
}
