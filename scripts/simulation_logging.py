# simulation_logging.py
import numpy as np
from utils import current_time_millis
from base_individuo import BaseIndividuo
import json

class BaseIndividuoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseIndividuo):
            return obj.__dict__
        return super().default(obj)

def initialize_log():
    with open("simulation_log.txt", "w") as log_file:
        log_file.write(f"Simulation started at {current_time_millis()}\n")

def log_message(message):
    with open("simulation_log.txt", "a") as log_file:
        log_file.write(f"{message}\n")
        log_file.flush()

def log_statistics(statistics, prefix="STATS"):
    # Convert int64 to regular Python integers
    for key, value in statistics.items():
        if isinstance(value, np.int64):
            statistics[key] = int(value)
    with open("simulation_log.txt", "a") as log_file:
        log_file.write(f"{prefix}: {json.dumps(statistics)}\n")
        log_file.flush()

def log_individual_status(individual_status, prefix="INDIVIDUAL"):
    with open("simulation_log.txt", "a") as log_file:
        log_file.write(f"{prefix}: {individual_status}\n")
        log_file.flush()

def report_death_statistics():
    print(f"Deaths by hunger: {BaseIndividuo.deaths_by_hunger}")
    print(f"Deaths by predator: {BaseIndividuo.deaths_by_predator}")


def log_death_statistics():
    log_message(f"Deaths by hunger: {BaseIndividuo.deaths_by_hunger}")
    log_message(f"Deaths by predator: {BaseIndividuo.deaths_by_predator}")
    total_deaths = BaseIndividuo.deaths_by_hunger + BaseIndividuo.deaths_by_predator
    log_message(f"Total deaths: {total_deaths}")


def finalize_log():
    with open("simulation_log.txt", "a") as log_file:
        log_file.write(f"Simulation ended at {current_time_millis()}\n")
