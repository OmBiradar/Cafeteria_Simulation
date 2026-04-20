// tests/test_entrance.cpp
#include <gtest/gtest.h>
#include <fstream>
#include <filesystem>
#include "entrance.h"

namespace fs = std::filesystem;

// A Test Fixture class to set up and tear down temporary files
class EntranceTest : public ::testing::Test
{
protected:
    fs::path temp_yaml_path = "temp_test_profiles.yaml";
    fs::path temp_csv_path = "temp_test_arrivals.csv";

    // This runs BEFORE every test
    void SetUp() override
    {
        // Create a dummy YAML file
        std::ofstream yaml_file(temp_yaml_path);
        yaml_file << "---\n"
                  << "config_1:\n"
                  << "  name: \"Test Mix\"\n"
                  << "  description: \"A test description.\"\n"
                  << "  probability_distribution:\n"
                  << "    - 1 : 0.5\n"
                  << "    - 2 : 0.5\n";
        yaml_file.close();

        // Create a dummy CSV/txt file
        std::ofstream csv_file(temp_csv_path);
        csv_file << "10:00 - 10:10, 5\n"
                 << "10:10 - 10:20, 12\n";
        csv_file.close();
    }

    // This runs AFTER every test
    void TearDown() override
    {
        // Clean up temporary files
        if (fs::exists(temp_yaml_path))
            fs::remove(temp_yaml_path);
        if (fs::exists(temp_csv_path))
            fs::remove(temp_csv_path);
    }
};

// Test the YAML Loading
TEST_F(EntranceTest, LoadGroupSizeProfiles_ValidFile)
{
    Entrance entrance;
    entrance.set_group_size_profiles_path(temp_yaml_path);

    // Act
    bool result = entrance.load_group_size_profiles();

    // Assert
    EXPECT_TRUE(result);
    // Since we can't easily inspect the private vectors directly without getters,
    // expecting true confirms the YAML parser didn't throw an exception.
}

TEST_F(EntranceTest, LoadGroupSizeProfiles_InvalidFile)
{
    Entrance entrance;
    entrance.set_group_size_profiles_path("does_not_exist.yaml");

    // Act
    bool result = entrance.load_group_size_profiles();

    // Assert
    EXPECT_FALSE(result); // Should fail gracefully
}

// Test the Arrival Loading
TEST_F(EntranceTest, LoadArrivalProfile_ValidFile)
{
    Entrance entrance;
    entrance.set_arrival_profile_path(temp_csv_path);

    // Act
    bool result = entrance.load_arrival_profile();

    // Assert
    EXPECT_TRUE(result);
}