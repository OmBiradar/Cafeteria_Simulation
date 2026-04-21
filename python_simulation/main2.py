import csv
import yaml
import heapq
import random
import os
import matplotlib.pyplot as plt
from collections import deque, Counter
import statistics

# --- Utility Functions ---


def to_hhmmss(seconds: int) -> str:
    """Converts raw seconds into HH:MM:SS format."""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_time_to_seconds(time_str: str) -> int:
    """Converts HH:MM string to seconds from start of day."""
    hours, minutes = map(int, time_str.strip().split(":"))
    return hours * 3600 + minutes * 60


def hhmmss_to_seconds(time_str: str) -> int:
    """Converts HH:MM:SS string back to seconds for graphing."""
    if not time_str or time_str == "N/A":
        return 0
    hours, minutes, seconds = map(int, time_str.strip().split(":"))
    return hours * 3600 + minutes * 60 + seconds


# --- Object-Oriented Simulation Classes ---


class CustomerGroup:
    """Holds data for a single group of customers."""

    def __init__(self, group_id: int, size: int, time_band: str):
        self.group_id = group_id
        self.size = size
        self.time_band = time_band
        self.served_by = None
        self.status = "Pending"  # Pending, Served, or Rejected

        # Times in whole seconds
        self.arrival_time = 0
        self.service_start_time = 0
        self.service_end_time = 0

    @property
    def in_queue_time(self) -> int:
        if self.status == "Rejected":
            return 0
        return self.service_start_time - self.arrival_time

    @property
    def service_time(self) -> int:
        if self.status == "Rejected":
            return 0
        return self.service_end_time - self.service_start_time

    @property
    def wait_time(self) -> int:
        if self.status == "Rejected":
            return 0
        return self.in_queue_time + self.service_time


class Event:
    """Represents an event in the timeline (Priority Queue)."""

    ARRIVAL = "ARRIVAL"
    SERVICE_START = "SERVICE_START"
    SERVICE_COMPLETE = "SERVICE_COMPLETE"

    def __init__(
        self,
        time: int,
        event_type: str,
        group: CustomerGroup = None,
        server_id: str = None,
    ):
        self.time = time
        self.event_type = event_type
        self.group = group
        self.server_id = server_id

    def __lt__(self, other):
        return self.time < other.time


class CafeteriaSimulation:
    """Main Discrete Event Simulation Engine."""

    def __init__(
        self,
        profile_name: str,
        arrivals_file: str,
        profiles_file: str,
        num_human: int = 1,
        num_kiosk: int = 1,
        human_cost: float = 343.0,
        kiosk_cost: float = 33.0,
        benefit_per_customer: float = 150.0,
    ):
        self.profile_name = profile_name
        self.arrivals_file = arrivals_file
        self.profiles_file = profiles_file

        self.num_human = num_human
        self.num_kiosk = num_kiosk
        self.human_cost_unit = human_cost
        self.kiosk_cost_unit = kiosk_cost
        self.benefit_per_customer = benefit_per_customer

        # Max Queue Size Logic
        self.max_queue_size = 5 * (self.num_human + self.num_kiosk)

        # Base Cost Calculation
        self.total_human_cost = self.num_human * self.human_cost_unit
        self.total_kiosk_cost = self.num_kiosk * self.kiosk_cost_unit
        self.cost = self.total_human_cost + self.total_kiosk_cost
        self.benefit = 0.0

        # Customer & Group Trackers
        self.total_customers_served = 0
        self.total_customers_rejected = 0
        self.total_groups_served = 0
        self.total_groups_rejected = 0

        # Setup Servers
        self.servers = {}
        for i in range(1, num_human + 1):
            self.servers[f"h{i}"] = {
                "type": "human",
                "busy": False,
                "mu": 4.9280,
                "sigma": 0.4836,
            }
        for i in range(1, num_kiosk + 1):
            self.servers[f"k{i}"] = {
                "type": "kiosk",
                "busy": False,
                "mu": 5.108,
                "sigma": 0.567,
            }

        # Simulation State
        self.timeline = []
        self.queue = deque()
        self.current_time = 0

        # Data tracking for CSV generation
        self.customer_data = []
        self.footprint_data = []
        self.queue_length_data = []
        self.arrivals_summary_data = []
        self.service_times_data = {sid: [] for sid in self.servers.keys()}
        self.server_stats = {
            sid: {"groups_served": 0, "customers_served": 0}
            for sid in self.servers.keys()
        }

        self.group_counter = 1

    def load_group_profile(self) -> tuple:
        with open(self.profiles_file, "r") as file:
            profiles = yaml.safe_load(file)
        if self.profile_name not in profiles:
            raise ValueError(
                f"Profile {self.profile_name} not found in {self.profiles_file}"
            )
        distribution = profiles[self.profile_name]["probability_distribution"]
        sizes = [list(item.keys())[0] for item in distribution]
        weights = [list(item.values())[0] for item in distribution]
        return sizes, weights

    def generate_arrivals(self):
        sizes, weights = self.load_group_profile()

        with open(self.arrivals_file, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                time_slot = row["time_slot"]
                people_in = int(row["people_in"])

                if people_in == 0:
                    continue

                start_time_str, end_time_str = time_slot.split(" - ")
                start_sec = parse_time_to_seconds(start_time_str)
                end_sec = parse_time_to_seconds(end_time_str)

                remaining_people = people_in
                groups_formed = 0
                total_people_formed = 0

                while remaining_people > 0:
                    size = random.choices(sizes, weights=weights, k=1)[0]
                    accept_group = False

                    if size <= remaining_people:
                        accept_group = True
                    else:
                        if remaining_people > (size / 2):
                            accept_group = True
                        else:
                            remaining_people = 0

                    if accept_group:
                        group = CustomerGroup(self.group_counter, size, time_slot)
                        self.footprint_data.append(
                            {
                                "time_band": time_slot,
                                "group_id": group.group_id,
                                "size": group.size,
                            }
                        )
                        arrival_time = random.randint(start_sec, end_sec - 1)
                        heapq.heappush(
                            self.timeline, Event(arrival_time, Event.ARRIVAL, group)
                        )

                        self.group_counter += 1
                        groups_formed += 1
                        total_people_formed += size
                        remaining_people -= size
                        if remaining_people < 0:
                            remaining_people = 0

                if groups_formed > 0:
                    self.arrivals_summary_data.append(
                        {
                            "time_band": time_slot,
                            "no_of_people": total_people_formed,
                            "no_of_groups": groups_formed,
                        }
                    )

    def record_queue_length(self, time_sec: int):
        self.queue_length_data.append(
            {"time": to_hhmmss(time_sec), "length": len(self.queue)}
        )

    def run(self):
        self.generate_arrivals()
        self.record_queue_length(0)

        while self.timeline:
            event = heapq.heappop(self.timeline)
            self.current_time = event.time

            if event.event_type == Event.ARRIVAL:
                self.handle_arrival(event)
            elif event.event_type == Event.SERVICE_START:
                self.handle_service_start()
            elif event.event_type == Event.SERVICE_COMPLETE:
                self.handle_service_complete(event)

    def handle_arrival(self, event: Event):
        group = event.group
        group.arrival_time = self.current_time

        # Rejection Logic: Max Queue Size reached
        if len(self.queue) >= self.max_queue_size:
            group.status = "Rejected"
            self.total_customers_rejected += group.size
            self.total_groups_rejected += 1

            # Record the rejected group immediately
            self.customer_data.append(
                {
                    "group_id": group.group_id,
                    "size": group.size,
                    "status": group.status,
                    "time_band": group.time_band,
                    "arrival_time": to_hhmmss(group.arrival_time),
                    "in_queue_time": "N/A",
                    "service_start_time": "N/A",
                    "service_time": "N/A",
                    "wait_time": "N/A",
                    "served_by": "N/A",
                }
            )
            return

        self.queue.append(group)
        self.record_queue_length(self.current_time)

        if any(not s["busy"] for s in self.servers.values()):
            heapq.heappush(self.timeline, Event(self.current_time, Event.SERVICE_START))

    def handle_service_start(self):
        if not self.queue:
            return

        available_server = None
        for sid, sdata in self.servers.items():
            if not sdata["busy"]:
                available_server = sid
                break

        if not available_server:
            return

        self.servers[available_server]["busy"] = True
        group = self.queue.popleft()
        self.record_queue_length(self.current_time)

        group.service_start_time = self.current_time
        group.served_by = available_server

        mu = self.servers[available_server]["mu"]
        sigma = self.servers[available_server]["sigma"]

        service_duration = int(round(random.lognormvariate(mu, sigma)))
        if service_duration <= 0:
            service_duration = 1

        completion_time = self.current_time + service_duration
        heapq.heappush(
            self.timeline,
            Event(completion_time, Event.SERVICE_COMPLETE, group, available_server),
        )

        if self.queue and any(not s["busy"] for s in self.servers.values()):
            heapq.heappush(self.timeline, Event(self.current_time, Event.SERVICE_START))

    def handle_service_complete(self, event: Event):
        group = event.group
        server_id = event.server_id
        group.service_end_time = self.current_time
        group.status = "Served"
        self.servers[server_id]["busy"] = False

        # Apply Benefit & Counts
        self.benefit += group.size * self.benefit_per_customer
        self.total_customers_served += group.size
        self.total_groups_served += 1

        self.customer_data.append(
            {
                "group_id": group.group_id,
                "size": group.size,
                "status": group.status,
                "time_band": group.time_band,
                "arrival_time": to_hhmmss(group.arrival_time),
                "in_queue_time": to_hhmmss(group.in_queue_time),
                "service_start_time": to_hhmmss(group.service_start_time),
                "service_time": to_hhmmss(group.service_time),
                "wait_time": to_hhmmss(group.wait_time),
                "served_by": group.served_by,
            }
        )

        self.service_times_data[server_id].append(
            {"group_id": group.group_id, "service_time": to_hhmmss(group.service_time)}
        )
        self.server_stats[server_id]["groups_served"] += 1
        self.server_stats[server_id]["customers_served"] += group.size

        if self.queue:
            heapq.heappush(self.timeline, Event(self.current_time, Event.SERVICE_START))

    def export_results(self, output_dir="output"):
        os.makedirs(output_dir, exist_ok=True)
        size_counts = Counter(d["size"] for d in self.footprint_data)

        # Process Time Band Served vs Rejected Data
        time_band_stats = {}
        for row in self.customer_data:
            tb = row["time_band"]
            if tb not in time_band_stats:
                time_band_stats[tb] = {"served": 0, "rejected": 0}
            if row["status"] == "Served":
                time_band_stats[tb]["served"] += 1
            elif row["status"] == "Rejected":
                time_band_stats[tb]["rejected"] += 1

        # --- CSV EXPORTS ---
        with open(
            os.path.join(output_dir, "customer_group_data.csv"), "w", newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "group_id",
                    "size",
                    "status",
                    "time_band",
                    "arrival_time",
                    "in_queue_time",
                    "service_start_time",
                    "service_time",
                    "wait_time",
                    "served_by",
                ],
            )
            writer.writeheader()
            writer.writerows(sorted(self.customer_data, key=lambda x: x["group_id"]))

        with open(
            os.path.join(output_dir, "served_vs_rejected.csv"), "w", newline=""
        ) as f:
            writer = csv.DictWriter(
                f, fieldnames=["time_band", "groups_served", "groups_rejected"]
            )
            writer.writeheader()
            for tb, stats in time_band_stats.items():
                writer.writerow(
                    {
                        "time_band": tb,
                        "groups_served": stats["served"],
                        "groups_rejected": stats["rejected"],
                    }
                )

        with open(os.path.join(output_dir, "footprint.csv"), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["time_band", "group_id", "size"])
            writer.writeheader()
            writer.writerows(self.footprint_data)

        with open(os.path.join(output_dir, "queue_length.csv"), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["time", "length"])
            writer.writeheader()
            writer.writerows(self.queue_length_data)

        with open(os.path.join(output_dir, "arrivals.csv"), "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["time_band", "no_of_people", "no_of_groups"]
            )
            writer.writeheader()
            writer.writerows(self.arrivals_summary_data)

        with open(
            os.path.join(output_dir, "group_size_distribution.csv"), "w", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["size", "count"])
            writer.writeheader()
            for size in sorted(size_counts.keys()):
                writer.writerow({"size": size, "count": size_counts[size]})

        with open(os.path.join(output_dir, "server_stats.csv"), "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["server_id", "groups_served", "customers_served"]
            )
            writer.writeheader()
            for sid, stats in self.server_stats.items():
                writer.writerow(
                    {
                        "server_id": sid,
                        "groups_served": stats["groups_served"],
                        "customers_served": stats["customers_served"],
                    }
                )

        # Output isolated service times per counter
        for sid, data_list in self.service_times_data.items():
            if (
                data_list
            ):  # Only generate files for counters that actually served someone
                file_path = os.path.join(output_dir, f"service_times_{sid}.csv")
                with open(file_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["group_id", "service_time"])
                    writer.writeheader()
                    writer.writerows(sorted(data_list, key=lambda x: x["group_id"]))

        with open(os.path.join(output_dir, "in_queue_times.csv"), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["arrival_time", "in_queue_time"])
            writer.writeheader()
            for d in sorted(
                self.customer_data, key=lambda x: hhmmss_to_seconds(x["arrival_time"])
            ):
                writer.writerow(
                    {
                        "arrival_time": d["arrival_time"],
                        "in_queue_time": d["in_queue_time"],
                    }
                )

        with open(os.path.join(output_dir, "wait_times.csv"), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["arrival_time", "wait_time"])
            writer.writeheader()
            for d in sorted(
                self.customer_data, key=lambda x: hhmmss_to_seconds(x["arrival_time"])
            ):
                writer.writerow(
                    {"arrival_time": d["arrival_time"], "wait_time": d["wait_time"]}
                )

        # --- GRAPH GENERATION ---

        # 1. Served vs Rejected Over Time Band Plot
        if time_band_stats:
            bands = list(time_band_stats.keys())
            served_cnt = [time_band_stats[b]["served"] for b in bands]
            rejected_cnt = [time_band_stats[b]["rejected"] for b in bands]

            x = range(len(bands))
            plt.figure(figsize=(12, 6))
            plt.bar(
                [i - 0.2 for i in x],
                served_cnt,
                width=0.4,
                label="Served Groups",
                color="mediumseagreen",
            )
            plt.bar(
                [i + 0.2 for i in x],
                rejected_cnt,
                width=0.4,
                label="Rejected Groups",
                color="crimson",
            )
            plt.xticks(x, bands, rotation=45, ha="right")
            plt.ylabel("Number of Groups")
            plt.title("Groups Served vs. Rejected Across the Day")
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "graph_served_vs_rejected.png"))
            plt.close()

        # 2. Arrivals Plot
        if self.arrivals_summary_data:
            bands = [d["time_band"] for d in self.arrivals_summary_data]
            people = [d["no_of_people"] for d in self.arrivals_summary_data]
            groups = [d["no_of_groups"] for d in self.arrivals_summary_data]

            x = range(len(bands))
            plt.figure(figsize=(12, 6))
            plt.bar(
                [i - 0.2 for i in x],
                people,
                width=0.4,
                label="No. of People",
                color="royalblue",
            )
            plt.bar(
                [i + 0.2 for i in x],
                groups,
                width=0.4,
                label="No. of Groups",
                color="darkorange",
            )
            plt.xticks(x, bands, rotation=45, ha="right")
            plt.ylabel("Count")
            plt.title("Cafeteria Arrivals per Time Band")
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "graph_arrivals.png"))
            plt.close()

        # 3. Queue Length Plot
        if self.queue_length_data:
            q_times = [
                hhmmss_to_seconds(d["time"]) / 3600 for d in self.queue_length_data
            ]
            q_lengths = [d["length"] for d in self.queue_length_data]

            plt.figure(figsize=(10, 5))
            plt.step(q_times, q_lengths, where="post", color="crimson")
            plt.title("Queue Length Over Time")
            plt.xlabel("Time of Day (Hours)")
            plt.ylabel("Number of Groups in Queue")
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "graph_queue_length.png"))
            plt.close()

        # 4. Group Size Distribution Plot
        if size_counts:
            sizes = sorted(list(size_counts.keys()))
            counts = [size_counts[s] for s in sizes]

            plt.figure(figsize=(8, 5))
            plt.bar(sizes, counts, color="orchid", edgecolor="black")
            plt.title("Group Size Distribution")
            plt.xlabel("Group Size")
            plt.ylabel("Frequency")
            plt.xticks(sizes)
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "graph_group_size_distribution.png"))
            plt.close()

        # 5. Server Stats Plot
        if self.server_stats:
            servers = list(self.server_stats.keys())
            groups_served = [self.server_stats[s]["groups_served"] for s in servers]
            customers_served = [
                self.server_stats[s]["customers_served"] for s in servers
            ]

            x = range(len(servers))
            plt.figure(figsize=(10, 6))
            plt.bar(
                [i - 0.2 for i in x],
                groups_served,
                width=0.4,
                label="Groups Served",
                color="mediumpurple",
            )
            plt.bar(
                [i + 0.2 for i in x],
                customers_served,
                width=0.4,
                label="Customers Served",
                color="lightseagreen",
            )
            plt.xticks(x, [s.upper() for s in servers])
            plt.ylabel("Count")
            plt.title("Server Utilization: Groups & Customers Served")
            plt.legend()
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "graph_server_stats.png"))
            plt.close()

        # 6. Graphs per individual counter
        for sid, data_list in self.service_times_data.items():
            if data_list:
                s_times = [hhmmss_to_seconds(d["service_time"]) for d in data_list]
                plt.figure(figsize=(10, 5))
                plt.hist(
                    s_times,
                    bins=15,
                    color="mediumseagreen",
                    edgecolor="black",
                    alpha=0.7,
                )

                type_label = "Human" if sid.startswith("h") else "Kiosk"
                plt.title(
                    f"Distribution of Service Times - Counter {sid.upper()} ({type_label})"
                )
                plt.xlabel("Service Time (Seconds)")
                plt.ylabel("Frequency")
                plt.grid(True, linestyle="--", alpha=0.7)
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f"graph_service_times_{sid}.png"))
                plt.close()

        # 7. Scatter Plot for In Queue Times Over Time
        served_data = [d for d in self.customer_data if d["status"] == "Served"]
        if served_data:
            arr_times_hours = [
                hhmmss_to_seconds(d["arrival_time"]) / 3600 for d in served_data
            ]
            iq_times_seconds = [
                hhmmss_to_seconds(d["in_queue_time"]) for d in served_data
            ]

            plt.figure(figsize=(10, 5))
            plt.scatter(
                arr_times_hours,
                iq_times_seconds,
                color="dodgerblue",
                alpha=0.6,
                edgecolors="black",
            )
            plt.title("In-Queue Time vs. Time of Day")
            plt.xlabel("Time of Day (Hours)")
            plt.ylabel("In-Queue Time (Seconds)")
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "graph_in_queue_times.png"))
            plt.close()

        # 8. Scatter Plot for Wait Times Over Time
        if served_data:
            arr_times_hours = [
                hhmmss_to_seconds(d["arrival_time"]) / 3600 for d in served_data
            ]
            wait_times_seconds = [
                hhmmss_to_seconds(d["wait_time"]) for d in served_data
            ]

            plt.figure(figsize=(10, 5))
            plt.scatter(
                arr_times_hours,
                wait_times_seconds,
                color="tomato",
                alpha=0.6,
                edgecolors="black",
            )
            plt.title("Total Wait Time vs. Time of Day")
            plt.xlabel("Time of Day (Hours)")
            plt.ylabel("Total Wait Time (Seconds)")
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "graph_wait_times.png"))
            plt.close()


class BatchSimulationTracker:
    """Collects and outputs summary statistics for multiple simulations."""

    def __init__(self, profit_percentage: float = 0.20):
        self.results = []
        self.profit_percentage = (
            profit_percentage  # Configurable profit percentage metric
        )

    def add_simulation_result(self, sim: CafeteriaSimulation):
        # Calculate Queue Stats
        q_lengths = [d["length"] for d in sim.queue_length_data]
        avg_q_length = sum(q_lengths) / len(q_lengths) if q_lengths else 0
        max_q_length = max(q_lengths) if q_lengths else 0

        # Calculate Wait Stats (Only for Served groups)
        wait_times = [
            hhmmss_to_seconds(d["wait_time"])
            for d in sim.customer_data
            if d["status"] == "Served"
        ]
        avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0
        max_wait = max(wait_times) if wait_times else 0

        # Calculate Net Profit based on benefit, percentage, and cost
        net_profit = (sim.benefit * self.profit_percentage) - sim.cost

        self.results.append(
            {
                "config_profile": sim.profile_name,
                "num_human": sim.num_human,
                "num_kiosk": sim.num_kiosk,
                "cost": sim.cost,
                "benefit": sim.benefit,
                "profit_percentage": self.profit_percentage,
                "net_profit": net_profit,
                "customers_served": sim.total_customers_served,
                "customers_not_served": sim.total_customers_rejected,
                "human_station_cost": sim.total_human_cost,
                "kiosk_station_cost": sim.total_kiosk_cost,
                "max_queue_capacity": sim.max_queue_size,
                "max_queue_length_reached": max_q_length,
                "avg_queue_length": round(avg_q_length, 2),
                "avg_wait_time_sec": round(avg_wait, 2),
                "max_wait_time_sec": max_wait,
            }
        )

    def export_overall_results(self, output_dir="results"):
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "overall_results.csv")

        with open(filepath, "w", newline="") as f:
            if not self.results:
                return
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
            writer.writeheader()
            writer.writerows(self.results)

        print(f"Overall Batch Results Exported to '{filepath}'.")


if __name__ == "__main__":
    # Initialize tracker with an example 20% profit margin
    tracker = BatchSimulationTracker(profit_percentage=0.20)

    for human_servers in range(1, 3):
        for kiosk_servers in range(1, 4):

            for config_no in range(1, 6):
                config_name = f"config_{config_no}"
                print(f"Running simulation with {config_name}...")

                sim = CafeteriaSimulation(
                    profile_name=config_name,
                    arrivals_file="data/avg_day_arrivals.csv",
                    profiles_file="config/group_size_profiles.yaml",
                    num_human=human_servers,
                    num_kiosk=kiosk_servers,
                )

                sim.run()

                # Add to the batch tracker
                tracker.add_simulation_result(sim)

                # Export individual sim logic
                sim.export_results(
                    output_dir=f"resultss/human{human_servers}_kiosk{kiosk_servers}_{config_name}"
                )

    # Finalize and export the combined overall results for all simulation configurations
    tracker.export_overall_results("resultss")
