import random
import pandas as pd

def moga_optimize(catalog: pd.DataFrame, generations=10, pop_size=5):
    population = []
    for _ in range(pop_size):
        individual = catalog.sample(frac=1).reset_index(drop=True).head(2)
        cost = random.uniform(0.1, 1.0)
        availability = random.uniform(0.8, 1.0)
        population.append({
            "selected_services": individual.to_dict(orient="records"),
            "cost": round(cost, 2),
            "availability": round(availability, 2)
        })
    return sorted(population, key=lambda x: (x['cost'], -x['availability']))
