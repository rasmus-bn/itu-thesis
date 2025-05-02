from dataclasses import dataclass
from typing import List


@dataclass
class WorldParams:
    id: int
    resource_count: int
    resource_radius: int
    min_dist: int
    max_dist: int


WORLDS: List[WorldParams] = [
    WorldParams(id=0, resource_count=50, resource_radius=10, min_dist=600, max_dist=1400),  # World 0: 200 small resources
    WorldParams(id=1, resource_count=10, resource_radius=100, min_dist=600, max_dist=1400),  # World 1: 30 medium resources
    WorldParams(id=2, resource_count=3, resource_radius=300, min_dist=600, max_dist=1400),  # World 2: 3 large resources
    WorldParams(id=3, resource_count=10, resource_radius=50, min_dist=400, max_dist=500),  # World 3: close by resources
    WorldParams(id=4, resource_count=10, resource_radius=50, min_dist=1300, max_dist=1400),  # World 4: far away located resources
    # WorldParams(id=5, resource_count=10, resource_radius=50, min_dist=500, max_dist=1000),  # World 5: Obstacles included
]