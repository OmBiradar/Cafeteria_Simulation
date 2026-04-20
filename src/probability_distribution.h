#pragma once

#include <vector>

class ProbabilityDistribution
{
public:
    virtual ~ProbabilityDistribution() = default;
    virtual int sample() const = 0;
};

class DiscreteProbabilityDistribution : public ProbabilityDistribution
{
};

class EmpiricalDistribution : public DiscreteProbabilityDistribution
{
private:
    std::vector<double> cumulative_probabilities;

public:
    EmpiricalDistribution() = default;
    bool conform(std::vector<double> &probabilities);
    int sample() const override;
};