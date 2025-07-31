import random
import pandas as pd

def moga_optimize(catalog: pd.DataFrame, generations=10, pop_size=5):
    convergence = {"generation": [], "avg_cost": [], "avg_availability": []}
    final_gen_data = []
    for g in range(generations):
        population = []
        for _ in range(pop_size):
            individual = catalog.sample(frac=1).reset_index(drop=True).head(2)
            cost = random.uniform(0.1, 1.0)
            availability = random.uniform(0.8, 1.0)
            latency = random.uniform(0.05, 0.3)  # Simulate latency
            population.append({
                "selected_services": individual.to_dict(orient="records"),
                "cost": round(cost, 2),
                "availability": round(availability, 2),
                "latency": round(latency, 3)
            })
        
        # Log convergence data
        avg_cost = sum(p['cost'] for p in population) / pop_size
        avg_availability = sum(p['availability'] for p in population) / pop_size
        convergence["generation"].append(g + 1)
        convergence["avg_cost"].append(avg_cost)
        convergence["avg_availability"].append(avg_availability)

        if g == generations - 1:
            final_gen_data = population

    # Save data for plots
    print("Saving convergence to /app/plot_data/convergence_all.csv")
    pd.DataFrame(convergence).to_csv("/app/plot_data/convergence_all.csv", index=False, mode='w', header=True)
    print("Saved convergence!")

    print("Saving final gen to /app/plot_data/final_generation_all.csv")
    pd.DataFrame(final_gen_data).to_csv("/app/plot_data/final_generation_all.csv", index=False, mode='w', header=True)
    print("Saved final generation!")

    # Return top 3 for API
    return sorted(final_gen_data, key=lambda x: (x['cost'], -x['availability']))[:3]
