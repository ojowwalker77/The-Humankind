#traits.py
from base_individuo import BaseIndividuo

class VisionIndividuo:
    @staticmethod
    def upgrade(ind):
        ind.visao += 3  # Slight nerf: Enhance vision by an additional 2 squares instead of 3.
        if not hasattr(ind, 'has_vision_gene'):
            ind.has_vision_gene = True
            BaseIndividuo.total_vision_individuals += 1
        return ind
        
class SpeedIndividuo:
    @staticmethod
    def upgrade(ind):
        ind.velocidade += 3  # Enhanced speed: Increase from 3 to 4 for a slight buff.
        if not hasattr(ind, 'has_speed_gene'):
            ind.has_speed_gene = True
            BaseIndividuo.total_speed_individuals += 1 
        return ind

class MemoryIndividuo:
    total_memory_individuals = 0  # Initialize class variable to track memory trait individuals

    @staticmethod
    def upgrade(ind):
        if not hasattr(ind, 'memory_gene'):
            ind.memory_gene = True
            ind.remembered_empty_squares = set()  # Initialize memory storage
            MemoryIndividuo.total_memory_individuals += 1  # Increment total individuals with memory trait
        return ind

    def update_after_move(self, current_square, food_locations):
        found_food = any(current_square == (food[0], food[1]) for food in food_locations)
        if not found_food:
            self.remembered_empty_squares.add(current_square)
            # Adjust to only keep the most recent 5 remembered squares
            if len(self.remembered_empty_squares) > self.memory_capacity:
                self.remembered_empty_squares = set(list(self.remembered_empty_squares)[-self.memory_capacity:])
