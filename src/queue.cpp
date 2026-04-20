#include "queue.h"
#include "customer.h"

bool Queue::initialize()
{
    in_queue_customers.clear();
    served_customers.clear();
    customer_log.clear();
    return true;
}

bool Queue::addCustomerGroup(std::shared_ptr<CustomerGroup> customer_group)
{
    if (!customer_group)
    {
        return false;
    }

    in_queue_customers.push_back(customer_group);
    customer_log.push_back(customer_group);
    return true;
}

bool Queue::serveCustomerGroup(const Time &current_time)
{
    if (in_queue_customers.empty())
    {
        return false;
    }

    auto customer_group = in_queue_customers.front();
    in_queue_customers.erase(in_queue_customers.begin());

    customer_group->updateServiceTime(current_time);
    served_customers.push_back(customer_group);

    return true;
}

bool Queue::isEmpty() const
{
    return in_queue_customers.empty();
}
