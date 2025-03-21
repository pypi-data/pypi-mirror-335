# DLWheel

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)]()

A lightweight deep learning library.

## Installation

### Prerequisites

### Editable Installation (Development Mode)
```bash
pip install -e .
```

### Stable Release
```bash
pip install dlwheel
```

## Getting Started

### Basic Usage
```python
from dlwheel import setup
from pprint import pprint

cfg = setup()
pprint(cfg)
```

### Enable Experiment Backup
```bash
# Run with automatic backup (default back up directory: ./logs)
python main.py --backup
```

## Configuration System

### YAML Configuration
```yaml
# config/default.yaml
training:
  batch_size: 32
  optimizer: adam
  learning_rate: 1e-3
```