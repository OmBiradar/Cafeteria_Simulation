#pragma once

#include "customer.h"
#include "probability_distribution.h"
#include "queue.h"
#include <vector>

class ServiceStation
{
private:
    EmpiricalDistribution GeneratorCurve;
    std::vector<CustomerGroup> customers_served;
    Queue station_queue;

public:
    ServiceStation() = default;
    ~ServiceStation() = default;
    virtual bool initialize() { return true; }
};

class HumanServiceStation : public ServiceStation
{
public:
    HumanServiceStation() = default;
    ~HumanServiceStation() = default;
    bool initialize() override { return ServiceStation::initialize(); }
};

class KioskServiceStation : public ServiceStation
{
public:
    KioskServiceStation() = default;
    ~KioskServiceStation() = default;
    bool initialize() override { return ServiceStation::initialize(); }
};