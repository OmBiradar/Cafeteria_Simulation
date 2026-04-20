#include "probability_distribution.h"
#include <stdexcept>

bool EmpiricalDistribution::conform(std::vector<double> &probabilities)
{
    if (probabilities.empty())
    {
        return false;
    }
    cumulative_probabilities.clear();
    cumulative_probabilities.reserve(probabilities.size());
    double cumulative_sum = 0.0;
    for (const auto &prob : probabilities)
    {
        cumulative_sum += prob;
        cumulative_probabilities.push_back(cumulative_sum);
    }
    return true;
}

int EmpiricalDistribution::sample() const
{
    if (cumulative_probabilities.empty())
    {
        throw std::runtime_error("Cumulative probabilities are not set.");
    }
    double random_value = static_cast<double>(rand()) / RAND_MAX;
    for (size_t i = 0; i < cumulative_probabilities.size(); ++i)
    {
        if (random_value < cumulative_probabilities[i])
        {
            return static_cast<int>(i);
        }
    }
    return static_cast<int>(cumulative_probabilities.size() - 1);
}