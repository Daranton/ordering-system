# Week 1: Python Core & Project Setup

**Goal:** Build a solid Python foundation and set up the project repository. By Friday you have a working CLI tool that creates, lists, and filters mock orders from a JSON file — all with type hints and clean project structure.

**Why this matters:** Everything in the next 11 weeks runs on these fundamentals. FastAPI leans heavily on type hints. SQLAlchemy needs you to understand classes and data structures. Docker Compose config is just YAML and file system awareness. Get this right and the rest flows naturally.

---

## Pre-Week Setup (Sunday or Day 0)

**Install your tools before the week starts so Monday is pure learning.**

### Tasks

- Install Python 3.12+ — use your system package manager or [python.org downloads](https://www.python.org/downloads/)
- Install Git — `sudo apt install git` on Ubuntu/Debian
- Choose an editor: [VS Code](https://code.visualstudio.com/) with the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) is the standard recommendation for beginners
- Install `mypy` globally to check your work: `pip install mypy`
- Create a GitHub account if you don't have one

### Verify everything works

```bash
python3 --version    # Should be 3.12+
git --version
mypy --version
```

---

## Monday — Python Fundamentals & Reading Day

**Goal:** Understand Python's core building blocks well enough to write small programs without constantly looking things up.

### What to read

Work through the official Python tutorial. Don't skim — type out every example and run it. Reading code is not the same as writing code.

| Topic | Source | Time |
|-------|--------|------|
| Data types, variables, strings, numbers | [Python Tutorial §3 — An Informal Introduction](https://docs.python.org/3/tutorial/introduction.html) | 45 min |
| Control flow: `if`, `for`, `while`, `match` | [Python Tutorial §4 — Control Flow](https://docs.python.org/3/tutorial/controlflow.html) | 60 min |
| Functions, default args, `*args`, `**kwargs` | [Python Tutorial §4.7–4.8](https://docs.python.org/3/tutorial/controlflow.html#defining-functions) | 45 min |
| Data structures: lists, dicts, sets, tuples | [Python Tutorial §5 — Data Structures](https://docs.python.org/3/tutorial/datastructures.html) | 60 min |

### Practice exercises

After each section, write a small script that uses what you just read. Examples:

1. A function that takes a list of prices and returns the total, average, and most expensive item
2. A dict that maps order statuses to descriptions — iterate it, filter it, update it
3. A function with keyword arguments that builds an "order" dict from parameters

### End of day checkpoint

You can comfortably write functions that accept arguments, work with dicts and lists, and use loops and conditionals without referencing the docs for basic syntax.

---

## Tuesday — Modules, Packages & Error Handling

**Goal:** Understand how Python organises code into files and packages, and how to handle things going wrong.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| Modules and packages | [Python Tutorial §6 — Modules](https://docs.python.org/3/tutorial/modules.html) | 45 min |
| Errors and exceptions, `try/except/finally`, raising | [Python Tutorial §8 — Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html) | 45 min |
| Classes — just the basics: `__init__`, methods, attributes | [Python Tutorial §9 — Classes](https://docs.python.org/3/tutorial/classes.html) (read §9.1–9.5 only) | 60 min |
| Reading and writing files, `with` statement | [Python Tutorial §7 — Input and Output](https://docs.python.org/3/tutorial/inputoutput.html) | 30 min |

### Practice exercises

1. Create two files: `models.py` with a simple `Order` class, and `main.py` that imports and uses it
2. Add validation to `Order.__init__` — raise `ValueError` if quantity is negative or status is invalid
3. Write a function that reads a JSON file, catches `FileNotFoundError` and `json.JSONDecodeError`, and returns a sensible default

### End of day checkpoint

You can split code across files, import between them, define classes with validation, and handle errors without your program crashing.

---

## Wednesday — Type Hints & Virtual Environments

**Goal:** Add type safety to your code (FastAPI requires this) and learn to isolate project dependencies.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| Type hints introduction | [Real Python — Python Type Checking](https://realpython.com/python-type-checking/) (read the first half up to "Type Comments") | 60 min |
| The `typing` module: `Optional`, `list`, `dict`, `Union` | [Python `typing` module docs](https://docs.python.org/3/library/typing.html) — scan the common types | 30 min |
| PEP 484 — the motivation behind type hints | [PEP 484](https://peps.python.org/pep-0484/) — read the introduction and rationale sections | 20 min |
| Virtual environments | [Python Tutorial §12 — Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html) | 20 min |
| `dataclasses` — typed data containers | [Python `dataclasses` docs](https://docs.python.org/3/library/dataclasses.html) | 30 min |

### Practice exercises

1. Go back to yesterday's `Order` class and rewrite it as a `@dataclass` with full type annotations
2. Create typed helper functions:
   - `generate_order_id() -> str` — returns a UUID string
   - `validate_status(status: str, valid_statuses: list[str]) -> bool`
   - `calculate_total(items: list[dict[str, float]]) -> float`
3. Set up a virtual environment for the project:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install mypy
   ```
4. Run `mypy --strict` on all your code and fix every error

### End of day checkpoint

All your code has type hints. `mypy --strict` passes with no errors. You understand what `Optional[str]` means vs `str`, and why `dict[str, Any]` is sometimes necessary.

---

## Thursday — Git & Project Structure

**Goal:** Set up the real project repo with a clean structure and start building the CLI tool.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| Git fundamentals: init, add, commit, branch, merge | [Git Handbook (GitHub)](https://docs.github.com/en/get-started/using-git/about-git) | 30 min |
| Writing good commit messages | [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — read the summary | 15 min |
| Python project structure | [Real Python — Python Application Layouts](https://realpython.com/python-application-layouts/) | 30 min |

### Project setup

Create this structure:

```
ordering-system/
├── README.md
├── pyproject.toml          # or requirements.txt for now
├── .gitignore
├── src/
│   └── utils/
│       ├── __init__.py
│       ├── ids.py           # ID generation (uuid4)
│       ├── validation.py    # Input validation helpers
│       └── models.py        # Order dataclass and related types
├── cli/
│   ├── __init__.py
│   └── main.py              # The CLI entry point
├── data/
│   └── orders.json          # Sample data file (auto-created by CLI)
└── tests/
    └── __init__.py
```

### Activities

1. Initialise the Git repo, create a `.gitignore` (use [gitignore.io](https://www.toptal.com/developers/gitignore) for Python)
2. Move all your existing code into the structure above
3. Make sure imports work: `from src.utils.models import Order`
4. Start building `cli/main.py` using `argparse`:
   - `python -m cli.main create --customer "Alice" --item "Widget" --quantity 3`
   - `python -m cli.main list`
   - `python -m cli.main list --status PENDING`
5. The CLI reads from and writes to `data/orders.json`
6. Commit after each meaningful change — aim for 5+ commits today

### End of day checkpoint

The project repo is clean, structured, and has meaningful Git history. The CLI can create orders and save them to JSON. Imports work across packages.

---

## Friday — Complete the CLI, Refactor & Polish

**Goal:** Finish the CLI tool, add filtering, make it robust, and ensure everything passes `mypy --strict`.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| `argparse` reference (if needed) | [Python `argparse` tutorial](https://docs.python.org/3/howto/argparse.html) | 20 min |
| `json` module | [Python `json` docs](https://docs.python.org/3/library/json.html) | 15 min |
| `enum` module — for order statuses | [Python `enum` docs](https://docs.python.org/3/library/enum.html) | 20 min |

### Activities

1. **Finish CLI commands:**
   - `create` — creates an order, assigns a UUID, sets status to `PENDING`, writes to JSON
   - `list` — prints all orders in a readable format
   - `list --status PENDING` — filters by status
   - `get <order_id>` — retrieves a single order by ID

2. **Harden the code:**
   - Use `enum.Enum` for order statuses instead of raw strings
   - Handle edge cases: missing file, invalid JSON, unknown status filter, order not found
   - All errors produce helpful messages, not stack traces

3. **Quality pass:**
   - Run `mypy --strict` — fix all issues
   - Read through your own code — rename anything unclear
   - Make sure every function has a one-line docstring

4. **Final commits:**
   - Clean up Git history
   - Write a short `README.md`: what the project is, how to set up, how to run the CLI
   - Push to GitHub

### End of day checkpoint

The CLI is complete and works reliably. The code is typed, documented, and structured cleanly. The repo is on GitHub with a README. You're ready for Week 2.

---

## Week 1 Deliverable Checklist

- [ ] Git repo on GitHub with meaningful commit history (10+ commits)
- [ ] Clean project structure with `src/`, `cli/`, `data/`, `tests/` directories
- [ ] `Order` dataclass with full type annotations
- [ ] Enum-based order statuses (`PENDING`, `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`)
- [ ] Utility functions: ID generation, validation — all typed
- [ ] CLI tool with `create`, `list`, `list --status`, `get` commands
- [ ] JSON file persistence (read/write orders)
- [ ] Error handling: missing files, invalid input, unknown IDs — all produce clean messages
- [ ] `mypy --strict` passes with zero errors
- [ ] `README.md` with setup and usage instructions

---

## Recommended Reading Order (Full Week)

If you prefer to front-load reading, here is the complete list in priority order:

1. [Python Tutorial §3–9](https://docs.python.org/3/tutorial/) — the core language
2. [Real Python — Python Type Checking](https://realpython.com/python-type-checking/) — essential for everything that follows
3. [Python `dataclasses` docs](https://docs.python.org/3/library/dataclasses.html) — your primary data modelling tool for now
4. [Python `argparse` tutorial](https://docs.python.org/3/howto/argparse.html) — for the CLI
5. [Git Handbook](https://docs.github.com/en/get-started/using-git/about-git) — version control fundamentals
6. [Real Python — Python Application Layouts](https://realpython.com/python-application-layouts/) — project structure patterns
7. [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — commit message discipline

---

## Looking Ahead

Next week you'll take the CLI's data model and expose it as a REST API using FastAPI. The `Order` dataclass becomes a Pydantic model. The JSON file becomes an in-memory dict (then Postgres in Week 3). Everything you build this week carries forward.
