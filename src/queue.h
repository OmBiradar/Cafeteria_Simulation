#pragma once

#include <vector>
#include <memory>
#include "utils.h"

class CustomerGroup;

class Queue
{
    std::vector<std::shared_ptr<CustomerGroup>> in_queue_customers;
    std::vector<std::shared_ptr<CustomerGroup>> served_customers;
    std::vector<std::shared_ptr<CustomerGroup>> customer_log;

public:
    Queue() = default;
    ~Queue() = default;

    bool initialize();
    bool addCustomerGroup(std::shared_ptr<CustomerGroup> customer_group);
    bool serveCustomerGroup(const Time &current_time);
    bool isEmpty() const;
};