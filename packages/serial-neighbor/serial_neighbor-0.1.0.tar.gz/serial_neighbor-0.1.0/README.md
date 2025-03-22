# serial-neighbor

A lightweight and fast implementation of spatial neighbor search using serialization encoding (like z-order and Hilbert curves). Designed for 3D point cloud applications, compatible with PyTorch.

## Installation
```bash
pip install serial-neighbor
```

## Usage Example
```python
from serial_neighbor_lib import serial_neighbor
import torch

points = torch.rand(1000, 3).cuda()
query_xyz = torch.rand(100, 3).cuda()
idx, dists = serial_neighbor(points, query_xyz, ["z"], k_neighbors=8)
print(idx.shape, dists.shape)
```