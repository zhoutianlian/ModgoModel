from numpy.random import *
from copy import copy


def monte_carlo(call_function, original_parameters: dict, random_sets: dict, simulate_times: int = 1000):
    results = []
    times = 0
    while times < simulate_times:
        parameters = copy(original_parameters)
        for random_parameter in random_sets:
            if random_sets[random_parameter]['Dist'] == 'Exponential':
                parameters[random_parameter] = exponential(parameters[random_parameter])
            elif random_sets[random_parameter]['Dist'] == 'Gamma':
                shape = random_sets[random_parameter]['Shape']
                scale = random_sets[random_parameter]['Scale']
                parameters[random_parameter] = gamma(shape, scale)
            elif random_sets[random_parameter]['Dist'] == 'Normal':
                scale = random_sets[random_parameter]['Sigma']
                parameters[random_parameter] = normal(parameters[random_parameter], scale)
            elif random_sets[random_parameter]['Dist'] == 'Poisson':
                parameters[random_parameter] = poisson(parameters[random_parameter])
            elif random_sets[random_parameter]['Dist'] == 'Uniform':
                low = random_sets[random_parameter]['Low']
                high = random_sets[random_parameter]['High']
                parameters[random_parameter] = uniform(low, high)

        result = call_function(parameters, random_process=True, scenario=False)
        results.append(result)
        times += 1

    return results
