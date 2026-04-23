# Ordering System

A command-line tool for creating and managing orders, backed by a JSON file.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install mypy
```

Run all commands from the project root.

## Usage

### Create an order

```bash
python -m cli.main create --customer "Alice" --item "Widget" --quantity 3
```

### List all orders

```bash
python -m cli.main list
```

### Filter by status

```bash
python -m cli.main list --status pending
```

### Get a single order

```bash
python -m cli.main get <order_id>
```

## Valid statuses

`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`, `disputed`

## Project structure

```
ordering-system/
├── cli/main.py          # CLI entry point (argparse)
├── src/utils/
│   ├── models.py        # Order dataclass, load/save helpers
│   ├── ids.py           # UUID generation
│   └── validation.py    # Status validation
├── data/orders.json     # Persisted orders
└── tests/
```

## Type checking

```bash
mypy --strict src/ cli/
```
