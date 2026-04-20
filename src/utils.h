#pragma once

#include <functional>
#include <string>
#include <sstream>
#include <iomanip>

using Function = std::function<void()>;

class Time
{
private:
    int hours;
    int minutes;
    int seconds;

public:
    Time() : hours(0), minutes(0), seconds(0) {}
    Time(int h, int m, int s) : hours(h), minutes(m), seconds(s) {}
    ~Time() = default;

    int getSeconds() const { return seconds; }
    int getMinutes() const { return minutes; }
    int getHours() const { return hours; }

    int toSeconds() const { return (hours * 3600) + (minutes * 60) + seconds; }
    float toMinutes() const { return (hours * 60.0f) + minutes + (seconds / 60.0f); }
    float toHours() const { return hours + (minutes / 60.0f) + (seconds / 3600.0f); }

    void addSeconds(int sec)
    {
        int total_seconds = this->toSeconds() + sec;
        hours = (total_seconds / 3600) % 24;
        minutes = (total_seconds % 3600) / 60;
        seconds = total_seconds % 60;
    }

    bool fromString(const std::string &time_str)
    {
        std::stringstream ss(time_str);
        char delimiter1, delimiter2;
        if (!(ss >> hours >> delimiter1 >> minutes >> delimiter2 >> seconds))
        {
            return false;
        }
        if (delimiter1 != ':' || delimiter2 != ':')
        {
            return false;
        }
        return true;
    }

    bool operator<(const Time &other) const
    {
        return (hours * 3600 + minutes * 60 + seconds) < (other.hours * 3600 + other.minutes * 60 + other.seconds);
    }

    bool operator>(const Time &other) const
    {
        return (hours * 3600 + minutes * 60 + seconds) > (other.hours * 3600 + other.minutes * 60 + other.seconds);
    }

    bool operator==(const Time &other) const
    {
        return hours == other.hours && minutes == other.minutes && seconds == other.seconds;
    }

    friend std::ostream &operator<<(std::ostream &os, const Time &time)
    {
        char fill = os.fill('0');
        os << std::setw(2) << time.hours << ":" << std::setw(2) << time.minutes << ":" << std::setw(2) << time.seconds;
        os.fill(fill);
        return os;
    }
};