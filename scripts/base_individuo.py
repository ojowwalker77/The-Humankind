import numpy as np
import random
from utils import current_time_millis

class BaseIndividuo:
    # Class-level statistics
    total_duelos = 0
    total_lifetime = 0
    total_individuals = 0
    dead_individuals = 0
    total_vision_individuals = 0
    total_speed_individuals = 0
    total_memory_individuals = 0
    deaths_by_hunger = 0
    deaths_by_predator = 0
    deaths_by_duel = 0

    
    BMR = 1.0  # Basic Metabolic Rate, calories burned at rest
    ACTIVITY_COSTS = {
            'moving': 0.2,  # Calorie cost per distance unit when moving
            'running': 0.5,  # Calorie cost per distance unit when running from predators
            'dueling': 2,  # Fixed calorie cost for engaging in a duel
            }
    
    def __init__(self, id, x, y, birth_time):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 10
        self.velocidade = 1  # Base speed in squares per second, consider adjustments for traits
        self.dano = 1  # Base damage per second
        self.visao = 1  # Base vision in squares
        self.reserva_calorica = 20  # Caloric reserve
        self.vivo = True
        self.distancia_percorrida2 = 0
        self.distancia_percorrida = 0 
        self.distance_traveled_since_last_activity = 0
        self.time_since_last_duel = 0
        self.birth_time = birth_time
        self.death_time = None
        self.lifespan = None
        self.food_eaten = 0
        self.total_hp_loss = 0
        self.total_cal_loss = 0
        self.total_hp_loss_from_duel = 0
        self.total_hp_loss_from_predator = 0
        self.hp_loss_from_hunger = 0
        self.cal_loss_from_movement = 0
        self.cal_loss_from_duel = 0
        self.activity_this_cycle = 'resting'

        BaseIndividuo.total_individuals += 1
        
    def distance_to(self, location):
        loc_x, loc_y = location
        return np.sqrt((self.x - loc_x) ** 2 + (self.y - loc_y) ** 2)

    def move(self, food_locations, size):
        if self.sees_food(food_locations):
            self.move_towards_food(food_locations, size)
        else:
            self.move_randomly(size)

    def move_randomly(self, size):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        dx, dy = random.choice(directions)

        self.x = max(0, min(self.x + dx, size - 1))
        self.y = max(0, min(self.y + dy, size - 1))
        self.distancia_percorrida += 1
        self.reserva_calorica -= 0.1

    def move_towards_food(self, food_locations, size):
        closest_food = self.find_closest_food(food_locations)
        if closest_food:
            food_x, food_y, food_cal = closest_food
            if (self.x, self.y) == (food_x, food_y):
                self.consume_food(food_cal)
                food_locations.remove(closest_food)
                self.move_randomly(size)
            else:
                dx = np.sign(food_x - self.x)
                dy = np.sign(food_y - self.y)
                self.x = max(0, min(self.x + dx, size - 1))
                self.y = max(0, min(self.y + dy, size - 1))
                self.distancia_percorrida += np.sqrt(dx**2 + dy**2)
                self.reserva_calorica -= 0.1

    def find_closest_food(self, food_locations):
        closest_food = None
        min_distance = float('inf')
        for food_x, food_y, food_cal in food_locations:
            distance = np.sqrt((self.x - food_x)**2 + (self.y - food_y)**2)
            if distance < min_distance and distance <= self.visao:
                min_distance = distance
                closest_food = (food_x, food_y, food_cal)
        return closest_food
    
    def move_on_danger(self, predator, size):
        if predator:
            dx = np.sign(self.x - predator.x)
            dy = np.sign(self.y - predator.y)
            self.x = max(0, min(self.x + dx, size - 1))
            self.y = max(0, min(self.y + dy, size - 1))
        else:
            self.move_randomly(size)

    def find_closest_predator(self, predators):
        closest_predator_info = None
        min_distance = float('inf')
        for predator in predators:
            distance = np.sqrt((self.x - predator.x) ** 2 + (self.y - predator.y) ** 2)
            if distance < min_distance and distance <= self.visao:
                min_distance = distance
                closest_predator_info = predator
        return closest_predator_info

    def consume_food(self, cal):
        self.food_eaten += 1
        self.reserva_calorica += cal

    def duel(self, outro, current_time):
        if current_time - self.time_since_last_duel >= 5:
            self.hp -= self.dano * 1
            outro.hp -= outro.dano * 1
            self.total_hp_loss += outro.dano * 1
            outro.total_hp_loss += self.dano * 1
            self.total_hp_loss_from_duel += outro.dano * 1
            outro.total_hp_loss_from_duel += self.dano * 1
            self.time_since_last_duel = current_time
            outro.time_since_last_duel = current_time
            if self.hp <= 0:
                self.cause_of_death = "duel"
            BaseIndividuo.total_duelos += 1
            
    def update_caloric_reserve(self):
            # Adjust caloric reserve based on activity
            activity_cost = {
                'moving': 0.5,  # Cost per unit distance
                'running': 0.8,  # Higher cost for running from predators
                'dueling': 2,  # Fixed cost for dueling
                'resting': 0.1,  # Basal metabolic rate when not engaged in other activities
            }
            
            cost = self.distancia_percorrida * activity_cost.get(self.activity_this_cycle, 0.1) + BaseIndividuo.BMR
            self.reserva_calorica -= cost
            
            # Reset distance traveled for the next cycle
            self.distancia_percorrida2 = self.distancia_percorrida
            self.distancia_percorrida = 0

            if self.reserva_calorica > 100:
                self.reserva_calorica = 98
            # Handle death by hunger
            if self.reserva_calorica <= 0:
                self.mark_as_dead(current_time_millis(), cause="hunger")

    def update(self, food_locations, predator_locations, predators, current_time, size, outros_individuos):
            if not self.vivo:
                return

            closest_predator = self.find_closest_predator(predators)
            if closest_predator and self.distance_to((closest_predator.x, closest_predator.y)) <= self.visao:
                self.move_on_danger(closest_predator, size)
            else:
                self.move(food_locations, size)
            self.general_updates(current_time, outros_individuos, predators)
            self.check_for_duels(outros_individuos, current_time)
            self.check_for_predator_encounters(predators, current_time)

    def general_updates(self, current_time, outros_individuos, predators):
        self.update_caloric_reserve()
        self.check_for_duels(outros_individuos, current_time)
        # Ensure the correct order of arguments when calling check_for_predator_encounters
        self.check_for_predator_encounters(predators, current_time)
        self.check_hunger()
        if self.hp <= 0 or self.reserva_calorica <= 0:
            self.mark_as_dead(current_time, self.cause_of_death if hasattr(self, 'cause_of_death') else "unknown")


    def duel_with_predator(self, predator, current_time):
        self.hp -= predator.damage
        self.total_hp_loss_from_predator += predator.damage
        if self.hp <= 0:
            self.mark_as_dead(current_time, cause="predator")


    def check_for_predator_encounters(self, predators, current_time):
        for predator in predators:
            if self.x == predator.x and self.y == predator.y:
                self.duel_with_predator(predator, current_time)

    def check_for_duels(self, outros_individuos, current_time):
        for outro in outros_individuos:
            if self.id != outro.id and self.x == outro.x and self.y == outro.y:
                self.duel(outro, current_time)

    def check_hunger(self):
            if self.reserva_calorica < 3:
                self.hp -= 0.1
                if self.hp <= 0:
                    self.cause_of_death = "hunger"

    def mark_as_dead(self, current_time, cause):
        if self.vivo:
            self.vivo = False
            self.death_time = current_time
            self.lifespan = current_time - self.birth_time
            BaseIndividuo.dead_individuals += 1

            # Increment appropriate death cause counter
            if cause == "hunger":
                BaseIndividuo.deaths_by_hunger += 1
            elif cause == "predator":
                BaseIndividuo.deaths_by_predator += 1
            elif cause == "duel":
                BaseIndividuo.deaths_by_duel += 1
            else:
                # Handle unknown cause if necessary
                pass
            print(f"Individual {self.id} died due to {cause} at time {current_time}.")

    def update_lifetime_stats(self):
        if self.death_time is not None:
            self.lifespan = self.death_time - self.birth_time
            BaseIndividuo.total_lifetime += self.lifespan
            BaseIndividuo.dead_individuals += 1
        else:
            self.lifespan = 0


    def sees_food(self, food_locations):
        for food in food_locations:
            if np.sqrt((self.x - food[0])**2 + (self.y - food[1])**2) <= self.visao:
                return True
        return False
    
    
