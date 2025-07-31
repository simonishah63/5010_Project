import pandas as pd
from datetime import datetime
import numpy as np

def generate_catalog(n_services=20):
    base_names = ['auth', 'user', 'order', 'billing', 'email', 'analytics', 'report', 'product', 'payment', 'shipping']
    
    services = []
    for i in range(n_services):
        name = f"{np.random.choice(base_names)}-service-{i}"
        service = {
            "service_name": name,
            "version": f"{np.random.randint(1, 3)}.{np.random.randint(0, 10)}.{np.random.randint(0, 10)}",
            "owner": f"Team {np.random.choice(['A', 'B', 'C', 'D'])}",
            "host": f"{name}.default.svc.cluster.local",
            "port": 8000 + i,
            "status": np.random.choice(["active", "inactive"], p=[0.8, 0.2]),
            "last_updated": datetime.utcnow(),
            "price": round(np.random.uniform(0.01, 0.15), 4),
            "availability": round(np.random.uniform(0.90, 0.999), 3),
            "latency": round(np.random.uniform(50, 300), 2)
        }
        services.append(service)
    
    return pd.DataFrame(services).set_index("service_name")
