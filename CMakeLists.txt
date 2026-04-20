cmake_minimum_required(VERSION 3.15)
project(CafeteriaSim VERSION 1.0 LANGUAGES CXX)

# Set C++23 standard
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add compiler warnings
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic")

# Gather all source files (excluding main.cpp so it doesn't conflict with tests)
file(GLOB SRC_FILES "src/*.cpp")

# --- 1. Main Executable Setup ---
add_executable(cafeteria_sim simulation_run/main.cpp ${SRC_FILES})
target_include_directories(cafeteria_sim PRIVATE src)

# Find and link yaml-cpp for the main executable
find_package(yaml-cpp REQUIRED)
target_link_libraries(cafeteria_sim PRIVATE yaml-cpp)

# --- 2. Google Test Framework Setup ---
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.12.1
)
FetchContent_MakeAvailable(googletest)

# --- 3. Test Executable Setup ---
# Compile the test files along with the source classes
add_executable(run_tests tests/test_entrance.cpp ${SRC_FILES})
target_include_directories(run_tests PRIVATE src)

# Link GTest, yaml-cpp, and pthread (required by GTest on Linux)
target_link_libraries(run_tests PRIVATE gtest_main gtest yaml-cpp pthread)

# Enable CTest integration
enable_testing()
add_test(NAME EntranceTests COMMAND run_tests)