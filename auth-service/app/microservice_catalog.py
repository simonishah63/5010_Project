import pandas as pd
from datetime import datetime
import numpy as np

def generate_catalog():
    services = [
        {
            "service_name": "auth-service",
            "version": "1.0.0",
            "owner": "Security Team",
            "host": "auth-service.default.svc.cluster.local",
            "port": 8000,
            "status": "active",
            "last_updated": datetime.utcnow(),
            "price": round(np.random.uniform(0.01, 0.1), 4),
            "availability": round(np.random.uniform(0.95, 0.999), 3),
            "latency": round(np.random.uniform(50, 200), 2)
        },
        {
            "service_name": "user-service",
            "version": "2.1.1",
            "owner": "User Management Team",
            "host": "user-service.default.svc.cluster.local",
            "port": 8001,
            "status": "active",
            "last_updated": datetime.utcnow(),
            "price": round(np.random.uniform(0.01, 0.1), 4),
            "availability": round(np.random.uniform(0.95, 0.999), 3),
            "latency": round(np.random.uniform(50, 200), 2)
        },
        {
            "service_name": "order-service",
            "version": "1.2.0",
            "owner": "Order Team",
            "host": "order-service.default.svc.cluster.local",
            "port": 8002,
            "status": "inactive",
            "last_updated": datetime.utcnow(),
            "price": round(np.random.uniform(0.01, 0.1), 4),
            "availability": round(np.random.uniform(0.95, 0.999), 3),
            "latency": round(np.random.uniform(50, 200), 2)
        }
    ]
    return pd.DataFrame(services).set_index("service_name")
