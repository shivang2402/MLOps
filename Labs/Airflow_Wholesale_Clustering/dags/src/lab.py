import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from kneed import KneeLocator
import pickle
import os
import base64

def load_data():
    print("Loading Wholesale Customers dataset...")
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/file.csv"))
    serialized_data = pickle.dumps(df)
    return base64.b64encode(serialized_data).decode("ascii")

def data_preprocessing(data_b64: str):
    data_bytes = base64.b64decode(data_b64)
    df = pickle.loads(data_bytes)
    df = df.dropna()
    clustering_data = df[["Fresh", "Milk", "Grocery", "Frozen", "Detergents_Paper", "Delicassen"]]
    scaler = StandardScaler()
    clustering_data_scaled = scaler.fit_transform(clustering_data)
    clustering_serialized = pickle.dumps(clustering_data_scaled)
    return base64.b64encode(clustering_serialized).decode("ascii")

def build_save_model(data_b64: str, filename: str):
    data_bytes = base64.b64decode(data_b64)
    df = pickle.loads(data_bytes)
    kmeans_kwargs = {"init": "random", "n_init": 10, "max_iter": 300, "random_state": 42}
    sse = []
    for k in range(2, 21):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(df)
        sse.append(kmeans.inertia_)
    kl = KneeLocator(range(2, 21), sse, curve="convex", direction="decreasing")
    optimal_k = kl.elbow if kl.elbow else 5
    print(f"Optimal k from elbow: {optimal_k}")
    best_model = KMeans(n_clusters=optimal_k, **kmeans_kwargs)
    best_model.fit(df)
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "wb") as f:
        pickle.dump(best_model, f)
    return sse

def load_model_elbow(filename: str, sse: list):
    output_path = os.path.join(os.path.dirname(__file__), "../model", filename)
    loaded_model = pickle.load(open(output_path, "rb"))
    kl = KneeLocator(range(2, 21), sse, curve="convex", direction="decreasing")
    print(f"Elbow confirmed at k={kl.elbow}")
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/test.csv"))
    pred = loaded_model.predict(df)[0]
    try:
        return int(pred)
    except Exception:
        return pred.item() if hasattr(pred, "item") else pred

def evaluate_model(data_b64: str, filename: str):
    data_bytes = base64.b64decode(data_b64)
    df = pickle.loads(data_bytes)
    output_path = os.path.join(os.path.dirname(__file__), "../model", filename)
    loaded_model = pickle.load(open(output_path, "rb"))
    labels = loaded_model.predict(df)
    score = silhouette_score(df, labels)
    print(f"Silhouette Score: {score:.4f}")
    return float(score)
