# filename: optimization/weighted_kmeans.py
import numpy as np
import math
from typing import List, Tuple
from schemas.io_models import HexCell

def run_weighted_kmeans(client_cells: List[HexCell], k: int, max_iterations: int = 100, tolerance: float = 1e-6) -> List[Tuple[float, float]]:
    """
    Executes a custom geographically weighted K-Means clustering.
    Uses Haversine distance metric for allocating clusters to account for spherical geometry of latitude/longitude.
    """
    if not client_cells:
        return []
    
    # 1. Extract coordinates and demand weights
    coords = np.array([[c.centroid_lat, c.centroid_lon] for c in client_cells])
    weights = np.array([c.local_demand_coefficient for c in client_cells])
    
    # Normalize weights to prevent scaling overflow
    total_weight = np.sum(weights)
    if total_weight > 0:
        normalized_weights = weights / total_weight
    else:
        normalized_weights = np.ones(len(client_cells)) / len(client_cells)
        
    n_samples = len(client_cells)
    if n_samples <= k:
        return [(float(pt[0]), float(pt[1])) for pt in coords]
        
    # 2. Initialize centroids using demand-weighted k-means++ probability distribution
    rng = np.random.default_rng(42)
    initial_idx = rng.choice(n_samples, size=k, replace=False, p=normalized_weights)
    centroids = coords[initial_idx]
    
    # 3. Iterative clustering loop
    for iteration in range(max_iterations):
        # Calculate Haversine distance matrix from all cells to all centroids
        # Distance matrix shape: (n_samples, k)
        distances = np.zeros((n_samples, k))
        
        for j in range(k):
            lat1 = np.radians(coords[:, 0])
            lon1 = np.radians(coords[:, 1])
            lat2 = np.radians(centroids[j, 0])
            lon2 = np.radians(centroids[j, 1])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            # Earth radius R = 6371.0 km
            distances[:, j] = 2 * 6371.0 * np.arcsin(np.sqrt(a))
            
        # Assign cells to nearest centroid
        assignments = np.argmin(distances, axis=1)
        
        # Update centroids to demand-weighted centers of assigned cells
        new_centroids = np.copy(centroids)
        for j in range(k):
            mask = (assignments == j)
            if np.any(mask):
                assigned_coords = coords[mask]
                assigned_weights = normalized_weights[mask]
                sum_w = np.sum(assigned_weights)
                if sum_w > 0:
                    new_centroids[j] = np.sum(assigned_coords * assigned_weights[:, np.newaxis], axis=0) / sum_w
                else:
                    new_centroids[j] = np.mean(assigned_coords, axis=0)
            else:
                # Re-initialize empty cluster to the cell with maximum distance to its nearest centroid
                min_dists = np.min(distances, axis=1)
                new_centroids[j] = coords[np.argmax(min_dists)]
                
        # Convergence check
        shift = np.sum(np.linalg.norm(new_centroids - centroids, axis=1))
        if shift < tolerance:
            break
        centroids = new_centroids
        
    return [(float(c[0]), float(c[1])) for c in centroids]
