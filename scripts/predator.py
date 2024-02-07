import random
import numpy as np

class Predator:
    def __init__(self, id, x, y, speed=4, vision=3, hp=200, damage=15, hunger_threshold=20):
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed  # Adjusted to use the given speed parameter
        self.vision = vision
        self.hp = hp
        self.damage = damage  # Damage the predator can inflict on prey
        self.hunger = 0
        self.hunger_threshold = hunger_threshold  # Threshold for when the predator starts losing HP due to hunger
        self.preys_eaten = 0

    def move(self, prey_locations, size):
        if not prey_locations:
            self.move_randomly(size)
            return
        # Determine the next action based on the visibility of prey
        closest_prey = self.find_closest_prey(prey_locations)
        if closest_prey:
            self.move_towards_prey(closest_prey, size)
        else:
            self.move_randomly(size)

    def move_randomly(self, size):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for _ in range(self.speed):  # Move multiple steps based on speed
            dx, dy = random.choice(directions)
            self.x = max(0, min(self.x + dx, size - 1))
            self.y = max(0, min(self.y + dy, size - 1))

    def move_towards_prey(self, prey, size):
        prey_x, prey_y = prey
        # Calculate direction and move towards prey based on predator's speed
        for _ in range(self.speed):
            dx = np.sign(prey_x - self.x)
            dy = np.sign(prey_y - self.y)
            self.x = max(0, min(self.x + dx, size - 1))
            self.y = max(0, min(self.y + dy, size - 1))

    def find_closest_prey(self, prey_locations):
        closest_prey = None
        min_distance = float('inf')
        for prey_x, prey_y in prey_locations:
            distance = np.sqrt((self.x - prey_x) ** 2 + (self.y - prey_y) ** 2)
            if distance <= self.vision and distance < min_distance:
                min_distance = distance
                closest_prey = (prey_x, prey_y)
        return closest_prey

    def eat_prey(self, prey):
        self.hp += self.damage  # Consider modifying this value based on the prey's attributes
        self.hunger = max(0, self.hunger - 20)  # Reduce hunger after eating
        self.preys_eaten += 1
        
    def update(self, prey_list, size):
        # First, update the predator's movement and actions
        prey_locations = [(prey.x, prey.y) for prey in prey_list]
        self.move(prey_locations, size)

        # Then, handle interactions with prey (eating or attacking)
        for prey in prey_list[:]:  # Copy the list to avoid modification during iteration
            if self.x == prey.x and self.y == prey.y:
                self.eat_prey(prey)
                prey_list.remove(prey)  # This assumes prey_list is accessible and modifiable

        # Manage hunger and potential death from starvation
        self.hunger += 1
        if self.hunger > self.hunger_threshold:
            self.hp -= 1  # Lose health due to starvation

        if self.hp <= 0:
            return "dead"  # Signal that the predator has died
        return "alive"  # Otherwise, indicate the predator is still alive
