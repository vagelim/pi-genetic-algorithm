#!/usr/bin/python3

import random
import time
from decimal import *

MAX_INT = 2147483647
PI = Decimal(3.141592653589793)
# Note: I couldn't get the precision any better than 15 digits past
# the decimal point. I think it's a fundamental limitation of floating
# point math: https://docs.python.org/3.1/tutorial/floatingpoint.html

def string_groups(string):
    return " ".join([string[i:i+3] for i in range(0, len(string), 3)])

UNGROUPED_PI = '{0:.15f}'.format(PI)
FORMATTED_PI = string_groups(UNGROUPED_PI)

def fitness(pi_approx):
    """ Gets the absolute distance between animal's approximation of pi
    and actual value of pi """
    return abs(Decimal(PI) -
               Decimal(pi_approx))  # distance from pi (to 30 digits)


class Animal():
    def __init__(self, numerator=None, denominator=None):
        """ Generates a random animal if no numerator and denominator
        are specified (as during reproduction) """
        self.numerator = numerator if(numerator) else random.randint(
            1, MAX_INT)
        self.denominator = denominator if(denominator) else random.randint(
            1, MAX_INT)
        self.age = 0
        self.fitness = fitness(self.get_pi())

    def get_pi(self):
        return Decimal(self.numerator) / Decimal(self.denominator)


class Config():
    def __init__(self):
        """ Sets the initial conditions for the world.
            It's fun to see how changing different parameters affects the
            accuracy of the pi approximation """
        self.max_age = 5
        self.max_generations = 100
        self.max_population = 10000  # for killing off by overcrowding
        self.initial_population = 300
        self.max_distance_from_pi = 1  # for killing 'weak' animals
        self.mutation_percentage = 0.000001

    def __str__(self):
        return 'World configuration: ' + str(self.__dict__) + '\n'


class World():
    def __init__(self, config):
        self.animals = []
        self.fill_world(config.initial_population)
        self.sort_animals()

    def fill_world(self, population):
        """ The initial adding of animals to a fresh world """
        while len(self.animals) < population:
            animal = Animal()
            self.animals.append(animal)

    def sort_animals(self):
        """ The animals who most closely approximate pi end up at the
        front of the world's animals list """
        self.animals.sort(key=lambda x: x.fitness)

    def get_parents(self, l):
        """ Gives us pairs of parents for making children """
        for i in range(0, len(l), 2):
            to_yield = l[i:i + 2]
            if len(to_yield) % 2 == 0:
                yield to_yield

    def reproduce_animals(self, mutation):
        """ Adds new animals to the world by producing one new child
        from pairs of existing animals; ignores odd ones out """
        parent_pairs = list(self.get_parents(self.animals))
        for pair in parent_pairs:
            child = self.new_child(pair[0], pair[1], mutation)
            self.animals.append(child)
        self.sort_animals()

    def new_child(self, father, mother, mutation):
        """ Appends a new animal to the world using a mix of two other
        animals' "genes", and then mutates the result to simulate, e.g.
        environmental radiation or DNA errors as in the real world """
        num = (father.numerator + mother.numerator) / 2
        den = (father.denominator + mother.denominator) / 2

        if random.randint(0, 1):  # flip a coin to add or subtract
            num = num * (1 + mutation)
        else:
            num = num * (1 - mutation)

        if random.randint(0, 1):
            den = den * (1 + mutation)
        else:
            den = den * (1 - mutation)

        return Animal(round(num), round(den))

    def kill_old_animals(self, age):
        remaining_animals = [i for i in self.animals if i.age < age]
        self.animals = remaining_animals

    def age_animals(self):
        """ Increase the age of every animal so that we can later kill
        off old animals """
        for animal in self.animals:
            animal.age += 1

    def kill_weak_animals(self, max_dist):
        """ Animals not meeting the fitness threshold of being close enough
        to pi will die """
        remaining_animals = [i for i in self.animals
                             if i.fitness < max_dist]
        self.animals = remaining_animals

    def kill_overcrowded(self, max_pop):
        """ Kills off the weakest animals when overcrowding occurs """
        if len(self.animals) > max_pop:
            list_slice_endpoint = round(len(self.animals) // 2)
            self.animals = self.animals[:list_slice_endpoint]


def print_world_status(generation, world):
    print('* {0} generations elapsed; world population: {1}'.
        format(generation, len(world.animals)))
    if len(world.animals) > 0:
        fittest = world.animals[0]
        print('* Fittest animal: ' + str(fittest.__dict__))
        fittest_pi = '{0:.15f}'.format(fittest.get_pi())
        grouped_fittest_pi = string_groups(fittest_pi)
        print('* {0} (this animal\'s pi)'.format(grouped_fittest_pi))
    else:
        print('Sorry, no animals are alive')
    print('* {0} (actual pi)'.format(FORMATTED_PI))
    print('')

if __name__ == '__main__':
    config = Config()
    print(config)
    world = World(config)

    generation = 0
    print_world_status(generation, world)

    while generation < config.max_generations:
        world.kill_old_animals(config.max_age)
        world.kill_weak_animals(config.max_distance_from_pi)
        world.reproduce_animals(config.mutation_percentage)
        world.kill_overcrowded(config.max_population)
        generation += 1
        world.age_animals()
        print_world_status(generation, world)

