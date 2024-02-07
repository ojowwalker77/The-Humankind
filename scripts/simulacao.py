import numpy as np
import random
from food import Food
from config import *
from utils import *
from simulation_logging import  *
from traits import VisionIndividuo, SpeedIndividuo, MemoryIndividuo
from base_individuo import BaseIndividuo
from predator import Predator

def assign_traits(individuo):
    for prob, trait_class in [(VISION_PROBABILITY, VisionIndividuo), (SPEED_PROBABILITY, SpeedIndividuo), (MEMORY_PROBABILITY, MemoryIndividuo)]:
        if random.random() < prob:
            individuo = trait_class.upgrade(individuo)
    return individuo

def initialize_individuals(num_individuos):
    return [assign_traits(BaseIndividuo(id=i, x=random.randint(0, SIMULATION_SIZE-1), y=random.randint(0, SIMULATION_SIZE-1), birth_time=current_time_millis())) for i in range(num_individuos)]

def respawn_food(frutas, num_respawn, simulation_size):
    frutas.extend(Food(x=random.randint(0, simulation_size-1), y=random.randint(0, simulation_size-1), calorias=10) for _ in range(num_respawn))

def initialize_predators(num_predators, simulation_size):
    return [Predator(id=i, x=random.randint(0, simulation_size-1), y=random.randint(0, simulation_size-1)) for i in range(num_predators)]

def calculate_statistics(individuos):
    if not individuos:
        return {"average_hp": 0, "average_calories": 0, "average_distance": 0, "total_duels": BaseIndividuo.total_duelos}

    living_individuals = [ind for ind in individuos if ind.vivo]
    stats_fields = ['hp', 'reserva_calorica', 'distancia_percorrida']
    stats = {}
    for field in stats_fields:
        values = [getattr(ind, field) for ind in living_individuals]
        stats[f'average_{field}'] = np.mean(values) if values else 0
    stats["total_duels"] = BaseIndividuo.total_duelos
    return stats

def log_predator_statistics(predators):
    total_prays_eaten = sum(predator.preys_eaten for predator in predators)
    print(f"Total prey consumed by predators: {total_prays_eaten}")

def mark_individuals_as_dead_and_calculate_lifespans(individuos, simulation_end_time):
    for ind in individuos:
        if ind.vivo: 
            ind.mark_as_dead(simulation_end_time, cause= "End of simulation")
        if ind.lifespan is None and ind.death_time is not None:
            ind.lifespan = ind.death_time - ind.birth_time
        elif ind.lifespan is None:
            ind.lifespan = simulation_end_time - ind.birth_time


def main_simulation_loop():
    initialize_log()
    individuos = initialize_individuals(NUM_INDIVIDUOS)
    predators = initialize_predators(NUM_PREDATORS, SIMULATION_SIZE)
    frutas = [Food(x=random.randint(0, SIMULATION_SIZE-1), y=random.randint(0, SIMULATION_SIZE-1), calorias=10) for _ in range(NUM_FRUTAS)]

    simulation_start_time = current_time_millis()
    last_log_time = simulation_start_time

    while (current_time_millis() - simulation_start_time) < DURATION * 1000:
        current_time = current_time_millis()
        predator_locations = [(predator.x, predator.y) for predator in predators]
        food_locations = [(f.x, f.y, f.calorias) for f in frutas]
        
        if (current_time - last_log_time) >= LOG_INTERVAL_SECONDS * 1000:
            elapsed_time = (current_time - simulation_start_time) / 1000
            stats = calculate_statistics(individuos)
            stats_str = json.dumps(stats)
            log_message(f"Simulation running: {elapsed_time:.2f} seconds elapsed. Statistics: {stats_str}")
            last_log_time = current_time

        for ind in individuos:
            if ind.vivo:
                outros_individuos = [o for o in individuos if o.id != ind.id]
                ind.update(food_locations, predator_locations, predators, current_time, SIMULATION_SIZE, outros_individuos)

        for predator in list(predators):
            predator.update(individuos, SIMULATION_SIZE)
            if predator.hp <= 0:
                predators.remove(predator)

        if (current_time - simulation_start_time) // 1000 % RESPAWN_INTERVAL == 0:
            respawn_food(frutas, RESPAWN_QUANTIDADE, SIMULATION_SIZE)

        if not any(ind.vivo for ind in individuos):
            break

    mark_individuals_as_dead_and_calculate_lifespans(individuos, current_time_millis())
    report_death_statistics()
    log_predator_statistics(predators)
    log_message("Simulation ended.")
    log_death_statistics()
    finalize_log()

    return individuos

if __name__ == "__main__":
    individuos = main_simulation_loop()
    individuals_no_traits = [ind for ind in individuos if not hasattr(ind, 'has_vision_gene') and not hasattr(ind, 'has_speed_gene') and not hasattr(ind, 'memory_gene')]
    individuals_vision = [ind for ind in individuos if hasattr(ind, 'has_vision_gene') and ind.has_vision_gene]
    individuals_speed = [ind for ind in individuos if hasattr(ind, 'has_speed_gene') and ind.has_speed_gene]
    individuals_memory = [ind for ind in individuos if hasattr(ind, 'memory_gene') and ind.memory_gene]
    
    group_stats, death_causes = calculate_group_statistics(individuos)
    for group_name, stats in group_stats.items():
        print(f"Stats for {group_name} group:")
        print(f"Average distance traveled: {stats['average_distance']:.2f}")
        print(f"Average fruits eaten: {stats['average_fruits_eaten']:.2f}")
        print(f"Average HP loss: {stats['average_hp_loss']:.2f}")
        print(f"Average caloric loss: {stats['average_cal_loss']:.2f}")
        print(f"Average Lifespan: {stats['average_lifespan']:.2f} seconds")
        print()

