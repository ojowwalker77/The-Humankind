import time

import numpy as np

def current_time_millis():
    return int(round(time.time() * 1000))

def log_statistics(statistics):
    with open("simulation_logs.txt", "a") as log_file:
        log_file.write(f"{statistics}\n")

def calculate_group_statistics(individuals):
    # Create a dictionary to hold stats for each group
    groups = {
        'no_traits': [],
        'vision': [],
        'speed': [],
        'memory': [],
        'visionANDspeed': [],
        'visionANDmemory': [],
        'memoryANDspeed': [],
        'allGenes': []
    }
    
    
    death_causes = {group: {'hunger': 0, 'predator': 0, 'duel': 0} for group in groups.keys()}


    # Populate the groups dictionary with individuals
    for ind in individuals:
        # Determine which group(s) the individual belongs to
        group_keys = []
        if hasattr(ind, 'has_vision_gene') and ind.has_vision_gene:
            group_keys.append('vision')
        if hasattr(ind, 'has_speed_gene') and ind.has_speed_gene:
            group_keys.append('speed')
        if hasattr(ind, 'memory_gene') and ind.memory_gene:
            group_keys.append('memory')

        # Determine combination groups
        if len(group_keys) == 3:
            groups['allGenes'].append(ind)
        elif len(group_keys) == 2:
            if 'vision' in group_keys and 'speed' in group_keys:
                groups['visionANDspeed'].append(ind)
            if 'vision' in group_keys and 'memory' in group_keys:
                groups['visionANDmemory'].append(ind)
            if 'speed' in group_keys and 'memory' in group_keys:
                groups['memoryANDspeed'].append(ind)
        elif len(group_keys) == 1:
            groups[group_keys[0]].append(ind)
        else:
            groups['no_traits'].append(ind)

        # Update death causes
        if hasattr(ind, 'cause_of_death'):
            for key in ['no_traits', 'vision', 'speed', 'memory', 'visionANDspeed', 'visionANDmemory', 'memoryANDspeed', 'allGenes']:
                if ind in groups[key]:
                    death_causes[key][ind.cause_of_death] += 1

    # Calculate and log statistics for each group
    group_stats = {}
    for group_name, members in groups.items():
        stats = {
            'average_distance': np.mean([ind.distancia_percorrida2 for ind in members]) if members else 0,
            'average_fruits_eaten': np.mean([ind.food_eaten for ind in members]) if members else 0,
            'average_hp_loss': np.mean([ind.total_hp_loss for ind in members]) if members else 0,
            'average_cal_loss': np.mean([ind.total_cal_loss for ind in members]) if members else 0,
            'average_lifespan': np.mean([ind.lifespan for ind in members if ind.lifespan is not None]) if members else 0
        }
        group_stats[group_name] = stats

    return group_stats, death_causes
