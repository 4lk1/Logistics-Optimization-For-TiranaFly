import numpy as np
from sklearn.cluster import KMeans
from typing import List, Tuple, Optional
from .models import DepotCandidate, OptimizationResult, DemandAssignment
import time

class WeightedKMeansOptimizer:
    """
    Population-weighted clustering for initial depot placement.
    Finds centroids that minimize the weighted squared distance to demand points.
    """

    def __init__(self, n_clusters: int = 10):
        self.n_clusters = n_clusters
        self.centroids: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None

    def optimize(self, h3_coords: np.ndarray, populations: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Runs the weighted K-Means algorithm.
        h3_coords: Nx2 array of (lat, lng)
        populations: N array of population counts
        """
        # Scikit-learn's KMeans supports sample_weight
        kmeans = KMeans(
            n_clusters=self.n_clusters,
            init='k-means++',
            n_init=10,
            max_iter=300,
            random_state=42
        )
        
        start_time = time.perf_counter()
        kmeans.fit(h3_coords, sample_weight=populations)
        end_time = time.perf_counter()
        
        self.centroids = kmeans.cluster_centers_
        self.labels = kmeans.labels_
        self.runtime = end_time - start_time
        
        return self.centroids, self.labels

    def get_results(self, h3_ids: List[str], h3_coords: np.ndarray, populations: np.ndarray) -> OptimizationResult:
        """Processes the clustering output into a standard OptimizationResult."""
        if self.centroids is None:
            raise ValueError("Must run optimize() before get_results()")

        depots = []
        for i, center in enumerate(self.centroids):
            depots.append(DepotCandidate(
                id=f"kmeans_depot_{i}",
                lat=center[0],
                lng=center[1]
            ))

        assignments = []
        total_pop_served = 0
        total_dist = 0.0
        max_dist = 0.0

        for idx, cluster_idx in enumerate(self.labels):
            depot = depots[cluster_idx]
            dist = self._haversine(h3_coords[idx][0], h3_coords[idx][1], depot.lat, depot.lng)
            
            pop = populations[idx]
            assignments.append(DemandAssignment(
                h3_id=h3_ids[idx],
                depot_id=depot.id,
                distance=dist,
                population_served=int(pop)
            ))
            
            total_pop_served += pop
            total_dist += dist * pop
            max_dist = max(max_dist, dist)

        avg_dist = total_dist / total_pop_served if total_pop_served > 0 else 0

        return OptimizationResult(
            method_name="Weighted K-Means",
            depots=depots,
            assignments=assignments,
            total_population_served=int(total_pop_served),
            total_cost=len(depots) * 50000.0, # Placeholder cost
            avg_distance=avg_dist,
            max_distance=max_dist,
            runtime_sec=self.runtime
        )

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        from math import radians, cos, sin, asin, sqrt
        R = 6371000  # meters
        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
        return R * 2 * asin(sqrt(a))
