import random
import pandas as pd
import numpy as np
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

catalog_global = None

def calculate_actual_cost(services: pd.DataFrame) -> float:
    """Calculate actual cost from service catalog"""
    return services['price'].sum() * 0.8

def calculate_actual_availability(services: pd.DataFrame) -> float:
    """Calculate actual availability (0-1)"""
    return services['availability'].product()

def calculate_actual_latency(services: pd.DataFrame) -> float:
    """Calculate actual latency (Worst-case latency)"""
    return services['latency'].max()

@lru_cache(maxsize=1000)
def cached_metrics(service_ids: tuple) -> tuple:
    """Memoized metric calculation for service combinations"""
    services = catalog_global.loc[list(service_ids)]
    return (
        calculate_actual_cost(services),
        calculate_actual_availability(services),
        calculate_actual_latency(services)
    )

def nsga2_sort(population: List[Dict]) -> List[Dict]:
    """NSGA-II non-dominated sorting with crowding distance"""
    # Implement non-dominated sorting
    fronts = [[]]
    for ind in population:
        ind['dominated_by'] = 0
        ind['dominates'] = []
        for other in population:
            if (ind['cost'] < other['cost'] and 
                ind['availability'] > other['availability'] and
                ind['latency'] < other['latency']):
                ind['dominates'].append(other)
            elif (other['cost'] < ind['cost'] and 
                  other['availability'] > ind['availability'] and
                  other['latency'] < ind['latency']):
                ind['dominated_by'] += 1
        if ind['dominated_by'] == 0:
            fronts[0].append(ind)
    
    # Crowding distance calculation
    for front in fronts:
        if len(front) < 3:
            for ind in front:
                ind['crowding'] = 0.0
            continue
        for metric in ['cost', 'availability', 'latency']:
            front.sort(key=lambda x: x[metric])
            front[0]['crowding'] = 1e9
            front[-1]['crowding'] = 1e9
            metric_range = front[-1][metric] - front[0][metric]
            if metric_range == 0:
                for i in range(1, len(front) - 1):
                    front[i]['crowding'] = 0.0
            else:
                for i in range(1, len(front) - 1):
                    front[i]['crowding'] = (front[i + 1][metric] - front[i - 1][metric]) / metric_range
    
    # Flatten fronts with crowding distance
    return sorted(population, key=lambda x: (x['dominated_by'], -x.get('crowding', 0)))

def tournament_selection(population: List[Dict], size: int) -> List[Dict]:
    """Tournament selection with size 2"""
    selected = []
    for _ in range(size):
        candidates = random.sample(population, 2)
        winner = min(candidates, key=lambda x: x['dominated_by'])
        selected.append(winner)
    return selected

def crossover(parent1: Dict, parent2: Dict) -> tuple:
    """Uniform crossover for service combinations"""
    services1 = pd.DataFrame(parent1['selected_services'])
    services2 = pd.DataFrame(parent2['selected_services'])
    
    # Take one service from each parent
    child_services = pd.concat([
        services1.sample(n=1),
        services2.sample(n=1)
    ]).drop_duplicates()
    
    return create_individual(child_services), create_individual(child_services.sample(frac=1))

def mutate(individual: Dict) -> Dict:
    """Mutation by replacing one random service"""
    services = pd.DataFrame(individual['selected_services'])
    if len(catalog_global) > len(services):
        # Replace one service
        services = services.sample(frac=1).head(1)
        new_service = catalog_global[~catalog_global.index.isin(services.index)].sample(1)
        mutated = pd.concat([services, new_service])
        return create_individual(mutated)
    return individual

def create_individual(services: pd.DataFrame = None) -> Dict:
    """Create an individual with actual metrics"""
    if services is None:
        services = catalog_global.sample(n=2)  # Select 2 services
    
    service_ids = tuple(sorted(services.index.tolist()))
    cost, availability, latency = cached_metrics(service_ids)
    
    return {
        "selected_services": services.to_dict(orient="records"),
        "cost": round(cost, 2),
        "availability": round(availability, 2),
        "latency": round(latency, 3),
        "dominated_by": 0,
        "crowding": 0
    }

def moga_optimize(catalog: pd.DataFrame, generations: int = 10, pop_size: int = 20) -> List[Dict]:
    """Multi-Objective Genetic Algorithm Optimizer"""
    global catalog_global  # Make catalog available to cached functions
    catalog_global = catalog.copy()
    
    # Initialize population
    with ThreadPoolExecutor() as executor:
        population = list(executor.map(create_individual, [None]*pop_size))
    
    convergence = {
        "generation": [],
        "avg_cost": [],
        "avg_availability": [],
        "min_cost": [],
        "max_availability": []
    }

    for g in range(generations):
        # NSGA-II sorting
        population = nsga2_sort(population)
        
        # Early termination check
        if g > 5 and len(convergence["avg_cost"]) > 5:
            if abs(convergence["avg_cost"][-1] - convergence["avg_cost"][-5]) < 0.01:
                break
        
        # Selection and reproduction
        parents = tournament_selection(population, pop_size//2)
        offspring = []
        for i in range(0, len(parents)-1, 2):
            child1, child2 = crossover(parents[i], parents[i+1])
            offspring.extend([mutate(child1), mutate(child2)])
        
        # New generation (elitism + offspring)
        population = population[:pop_size//2] + offspring[:pop_size//2]
        
        # Log convergence
        convergence["generation"].append(g + 1)
        convergence["avg_cost"].append(np.mean([i['cost'] for i in population]))
        convergence["avg_availability"].append(np.mean([i['availability'] for i in population]))
        convergence["min_cost"].append(min(i['cost'] for i in population))
        convergence["max_availability"].append(max(i['availability'] for i in population))

    # Save results
    pd.DataFrame(convergence).to_csv("/app/plot_data/convergence_all.csv", index=False)
    pd.DataFrame(population).to_csv("/app/plot_data/final_generation_all.csv", index=False)
    
    # Return Pareto-optimal solutions
    pareto_front = [ind for ind in population if ind['dominated_by'] == 0]
    return sorted(pareto_front, key=lambda x: (x['cost'], -x['availability']))[:3]