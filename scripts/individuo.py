import numpy as np
import random
import time

class Individuo:
    # Class-level statistics
    total_duelos = 0
    total_lifetime = 0
    total_vision_lifetime = 0
    total_speed_lifetime = 0
    total_both_lifetime = 0
    total_individuals = 0
    total_individuals = 0
    total_vision = 0
    total_speed = 0
    total_both = 0
    total_vision_individuals = 0  # Initialize the missing attribute
    total_speed_individuals = 0  # Initialize the missing attribute
    total_both_individuals = 0  # Initialize the missing attribute

    def __init__(self, id, x, y, birth_time):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 10
        self.velocidade = 1  # sqr/s
        self.dano = 1  # hp/s
        self.visao = 1       # sqr
        self.audicao = 1  # sqr
        self.resistencia_fisica = 0  # shield
        self.resistencia_mental = 0  # shield
        self.reserva_calorica = 10  # cal
        self.vivo = True
        self.distancia_percorrida = 0
        self.time_since_last_duel = birth_time
        self.has_vision_gene = False
        self.has_speed_gene = False
        self.birth_time = birth_time
        self.death_time = None
        self.food_eaten = 0

        if random.random() < 0.25:
            self.visao += 5
            self.has_vision_gene = True
            Individuo.total_vision_individuals += 1 
        if random.random() < 0.25:
            self.velocidade += 5
            self.has_speed_gene = True
            Individuo.total_speed_individuals += 1  
        if self.has_vision_gene and self.has_speed_gene:
            Individuo.total_both_individuals += 1  

        Individuo.total_individuals += 1
            
    def check_status(self, current_time):
        if not self.vivo and self.death_time is None:
            self.death_time = current_time
            lifespan = self.death_time - self.birth_time
            Individuo.total_lifetime += lifespan
            if self.has_vision_gene:
                Individuo.total_vision_lifetime += lifespan
            if self.has_speed_gene:
                Individuo.total_speed_lifetime += lifespan
            if self.has_vision_gene and self.has_speed_gene:
                Individuo.total_both_lifetime += lifespan
        
    def move_based_on_encouragement(self, size):
        probability_of_moving = 1.0
        if self.reserva_calorica > 30:
            probability_of_moving = 0.5
        elif self.reserva_calorica < 5:
            probability_of_moving = 1.5
        elif self.reserva_calorica < 2:
            probability_of_moving = 2.0

        if random.random() <= min(1.0, probability_of_moving):
            move_distance = self.velocidade
            dx = random.choice([-move_distance, 0, move_distance])
            dy = random.choice([-move_distance, 0, move_distance]) if dx == 0 else 0

            self.x = max(0, min(self.x + dx, size - 1))
            self.y = max(0, min(self.y + dy, size - 1))
            self.distancia_percorrida += move_distance
            self.reserva_calorica -= 0.1


    def move_towards_food(self, food_locations, size):
        closest_food = self.find_closest_food(food_locations)
        if closest_food:
            food_x, food_y, food_cal = closest_food
            dx = np.sign(food_x - self.x)
            dy = np.sign(food_y - self.y)
            if dx != 0 and dy != 0:  # Diagonal movement adjustment
                if random.random() < 0.5:
                    dx = 0
                else:
                    dy = 0

            self.x = max(0, min(self.x + dx, size - 1))
            self.y = max(0, min(self.y + dy, size - 1))
            self.distancia_percorrida += 1
            self.reserva_calorica -= 0.1  # Adjusted cost of movement

            # Check if the individual has reached the food
            if (self.x, self.y) == (food_x, food_y):
                self.consume_food(food_cal)
                # Remove the consumed food from the food_locations list
                food_locations.remove(closest_food)  # Assumes food_locations is mutable and passed by reference

            
    def consume_food(self, cal):
        self.food_eaten += 1
        self.reserva_calorica += cal
                           
    def update(self, food_locations, current_time, size, outros_individuos):
        if not self.vivo:
            return

        # Decide whether to move towards food or wander randomly
        if self.sees_food(food_locations):
            self.move_towards_food(food_locations, size)
        else:
            self.move_based_on_encouragement(size)

        # Energy consumption and health checks
        self.reserva_calorica -= 1 / 30  # Passive energy loss per second
        self.check_for_duels(outros_individuos, current_time)
        self.check_hunger()

        if self.hp <= 0:
            self.mark_as_dead(current_time)

          
    def mark_as_dead(self, current_time):
        if not self.death_time:  # Ensure this is only done once
          self.vivo = False
          self.death_time = current_time
          self.update_lifetime_stats()

    def update_lifetime_stats(self):
      if not self.death_time:
        return  
    
      lifespan = self.death_time - self.birth_time
      Individuo.total_lifetime += lifespan
      Individuo.total_individuals += 1
    
      if self.has_vision_gene:
        Individuo.total_vision_lifetime += lifespan
        Individuo.total_vision_individuals += 1
      if self.has_speed_gene:
        Individuo.total_speed_lifetime += lifespan
        Individuo.total_speed_individuals += 1
      if self.has_vision_gene and self.has_speed_gene:
        Individuo.total_both_lifetime += lifespan
        Individuo.total_both_individuals += 1
            
    @classmethod
    def incrementar_duelos(cls):
        cls.total_duelos += 1

    def duel(self, outro, current_time):
        if current_time - self.time_since_last_duel >= 5:
            self.hp -= self.dano * 3
            outro.hp -= outro.dano * 3
            self.reserva_calorica -= 2
            outro.reserva_calorica -= 2
            self.time_since_last_duel = current_time
            outro.time_since_last_duel = current_time
            
            Individuo.incrementar_duelos()
            
    def sees_food(self, food_locations):
        for food in food_locations:
            if np.sqrt((self.x - food[0])**2 + (self.y - food[1])**2) <= self.visao:
                return True
        return False
    def check_status_and_update_lifetime(self, current_time):
        if self.vivo:
            return
        if self.death_time is None:
            self.death_time = current_time
            lifespan = self.death_time - self.birth_time
            Individuo.total_lifetime += lifespan
            if self.has_vision_gene:
                Individuo.total_vision_lifetime += lifespan
            if self.has_speed_gene:
                Individuo.total_speed_lifetime += lifespan
            if self.has_vision_gene and self.has_speed_gene:
                Individuo.total_both_lifetime += lifespan
                
    @classmethod
    def print_final_stats(cls):
    # Calculate averages based on the number of individuals with respective genes
      avg_lifetime = cls.total_lifetime / cls.total_individuals
      avg_vision_lifetime = cls.total_vision_lifetime / cls.total_vision_individuals 
      avg_speed_lifetime = cls.total_speed_lifetime / cls.total_speed_individuals
      avg_both_lifetime = cls.total_both_lifetime / cls.total_both_individuals if cls.total_both_individuals > 0 else 0  # Check if total_both_individuals > 0 to avoid division by zero
    
    # Calculate averages for individuals without any special genes
      avg_lifetime_without_genes = (cls.total_lifetime - cls.total_both_lifetime) / (cls.total_individuals - cls.total_both_individuals) if cls.total_both_individuals > 0 else avg_lifetime
      avg_vision_lifetime_without_genes = (cls.total_vision_lifetime - cls.total_both_lifetime) / (cls.total_vision_individuals - cls.total_both_individuals) if cls.total_both_individuals > 0 else avg_vision_lifetime
      avg_speed_lifetime_without_genes = (cls.total_speed_lifetime - cls.total_both_lifetime) / (cls.total_speed_individuals - cls.total_both_individuals) if cls.total_both_individuals > 0 else avg_speed_lifetime

      print("\nFinal Statistics:")
      print(f"Average Lifespan: {avg_lifetime:.2f} seconds")
      print(f"Average Lifespan with Vision Gene: {avg_vision_lifetime:.2f} seconds")
      print(f"Average Lifespan with Speed Gene: {avg_speed_lifetime:.2f} seconds")
      print(f"Average Lifespan with Both Genes: {avg_both_lifetime:.2f} seconds")
      print(f"Average Lifespan without Special Genes: {avg_lifetime_without_genes:.2f} seconds")
      


