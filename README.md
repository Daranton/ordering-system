# Ordering System

A command-line tool for creating and managing orders, backed by a JSON file.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest mypy
```

Run all commands from the project root.

## Usage

### Create an order

```bash
python -m cli.main create --customer "Alice" --item "Widget" --quantity 3
```

```
Created order 3f2a1b4c-8e9d-4f0a-b1c2-d3e4f5a6b7c8
```

### List all orders

```bash
python -m cli.main list
```

```
  3f2a1b4c-8e9d-4f0a-b1c2-d3e4f5a6b7c8  customer=Alice  item=Widget  qty=3  status=pending
```

### Filter by status

```bash
python -m cli.main list --status shipped
```

```
  7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d  customer=Bob  item=Gadget  qty=1  status=shipped
```

Passing an unrecognised status prints an error and exits:

```bash
python -m cli.main list --status unknown
```

```
Unknown status 'unknown'. Valid values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled', 'disputed']
```

### Get a single order

```bash
python -m cli.main get 3f2a1b4c-8e9d-4f0a-b1c2-d3e4f5a6b7c8
```

```
Order('3f2a1b4c-8e9d-4f0a-b1c2-d3e4f5a6b7c8', customer='Alice', item='Widget', qty=3, amount=0.0, status='pending')
```

If the order ID does not exist, the command exits with code 1:

```
Order '3f2a1b4c-...' not found.
```

## Valid statuses

`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`, `disputed`

## Testing

```bash
python -m pytest tests/ -v
```

## Type checking

```bash
python -m mypy src/ cli/ tests/
```

## Project structure

```
ordering-system/
├── cli/main.py          # CLI entry point (argparse)
├── src/utils/
│   ├── models.py        # Order dataclass, OrderStatus enum, load/save helpers
│   ├── ids.py           # UUID generation
│   └── validation.py    # Status validation
├── data/orders.json     # Persisted orders
└── tests/
    ├── test_models.py   # Order dataclass and JSON persistence
    ├── test_ids.py      # ID generation
    ├── test_cli.py      # CLI command functions
    └── test_validation.py  # Status validation
```
