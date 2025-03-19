# MyPackage

This package provides functionality for CUDA Graph capturing in PyTorch. It includes a warm-up function and CUDA Graph capture function to optimize inference execution.

## Installation

To install this package, run the following command:

```sh
pip install graph_mlsys
```

Or install from the local build:

```sh
pip install dist/graph_mlsys-0.1.0-py3-none-any.whl
```

## Usage

```python
import torch
from graph_mlsys.graph_capture import get_graph

model = torch.nn.Linear(10, 10).cuda()
input_tensor = torch.randn(1, 10).cuda()

graph, static_output = get_graph(model, input_tensor)
```

## License

This project is licensed under the MIT License.

