#pragma once
#include "probability_distribution.h"
#include <vector>
#include <utility>
#include <stdexcept>

template <typename T>
class WeightedSampler
{
private:
    std::vector<double> probabilities;
    std::vector<T> items;
    EmpiricalDistribution distribution;

public:
    WeightedSampler() = default;
    ~WeightedSampler() = default;
    bool add_items(std::vector<std::pair<T, double>> item_prob_pairs)
    {
        items.clear();
        probabilities.clear();
        items.reserve(item_prob_pairs.size());
        probabilities.reserve(item_prob_pairs.size());
        for (const auto &pair : item_prob_pairs)
        {
            items.push_back(pair.first);
            probabilities.push_back(pair.second);
        }
        distribution.conform(probabilities);
        return true;
    }
    T sample() const
    {
        if (items.empty() || probabilities.empty())
        {
            throw std::runtime_error("No items or probabilities to sample from.");
        }
        int index = distribution.sample();
        return items[index];
    }
};
