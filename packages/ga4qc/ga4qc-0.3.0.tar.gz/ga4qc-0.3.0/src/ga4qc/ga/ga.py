import random
from typing import List

from ga4qc.mutation import IMutation
from ga4qc.crossover import ICrossover
from ga4qc.processors import ICircuitProcessor
from ga4qc.selection import ISelection, BestSelection
from ga4qc.seeder import ISeeder
from ga4qc.callback import ICallback

from ga4qc.params import GAParams


class GA:

    seeder: ISeeder
    mutations: List[IMutation]
    crossovers: List[ICrossover]
    processors: List[ICircuitProcessor]
    selection: ISelection

    best_selection: ISelection

    before_generation_callbacks: List[ICallback]
    after_generation_callbacks: List[ICallback]
    on_completion_callbacks: List[ICallback]

    def __init__(
        self,
        seeder: ISeeder,
        mutations: List[IMutation],
        crossovers: List[ICrossover],
        processors: List[ICircuitProcessor],
        selection: ISelection,
    ):
        # TODO: Add default values for unspecified
        # operators.
        self.seeder = seeder
        self.mutations = mutations
        self.crossovers = crossovers
        self.processors = processors
        self.selection = selection

        self.best_selection = BestSelection()
        self.before_generation_callbacks = []
        self.after_generation_callbacks = []
        self.on_completion_callbacks = []

    def on_before_generation(self, callback: ICallback) -> None:
        self.before_generation_callbacks.append(callback)

    def on_after_generation(self, callback: ICallback) -> None:
        self.after_generation_callbacks.append(callback)

    def on_completion(self, callback: ICallback) -> None:
        self.on_completion_callbacks.append(callback)

    def run(
        self,
        params: GAParams
    ):
        population = self.seeder.seed(params.population_size)

        for generation in range(1, params.generations + 1):
            for callback in self.before_generation_callbacks:
                callback(population, generation)

            if generation == 1:
                elite = []
            else:
                elite = self.best_selection.select(
                    population, k=params.elitism_count, generation=generation)

            offspring = [circuit.copy() for circuit in population]

            # Shuffle to avoid crossover in the same proximity across
            # generations.
            random.shuffle(offspring)

            for crossover in self.crossovers:
                for circuit1, circuit2 in zip(offspring[:-1], offspring[1:]):
                    if random.random() < crossover.prob:
                        crossover.cross(circuit1, circuit2, generation)

            for mutation in self.mutations:
                for circuit in offspring:
                    if random.random() < mutation.prob:
                        mutation.mutate(circuit, generation)

            # Ensure that no old unitaries or fitness
            # values remain in a changed circuit.
            for circuit in offspring:
                circuit.reset()

            for processor in self.processors:
                processor.process(offspring, generation)

            population = elite + self.selection.select(
                offspring, k=params.population_size - len(elite), generation=generation
            )

            for callback in self.after_generation_callbacks:
                callback(population, generation)

        for callback in self.on_completion_callbacks:
            callback(population, generation)
