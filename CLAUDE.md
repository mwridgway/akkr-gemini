# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **CS2 Demo Analyzer** - a Python application for parsing Counter-Strike 2 demo files and calculating strategic gameplay metrics. The project follows **Clean Architecture** principles with a modular, layered design optimized for analytical workloads.

## Core Commands

### Environment Setup
```bash
# Install dependencies (first time)
poetry install

# Activate virtual environment
poetry shell
```

### Running the Application
```bash
# Analyze a demo file (from within poetry environment)
poetry run python -m src.cs2_analyzer.main path/to/demo.dem

# Or, after activating the shell
python -m src.cs2_analyzer.main path/to/demo.dem
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_metrics.py

# Run with verbose output
poetry run pytest -v

# Run specific test function
poetry run pytest tests/test_metrics.py::test_calculate_ttfk
```

## Architecture

The codebase follows **Clean Architecture** with strict layering and the **Dependency Inversion Principle**:

### Layer Structure
```
┌─────────────────────────────────────────┐
│  main.py (CLI Entry Point)              │
├─────────────────────────────────────────┤
│  application/                            │
│    - services.py (Use Cases)             │
│    - metrics.py (Metric Calculations)    │
│    - interfaces.py (Abstractions)        │
├─────────────────────────────────────────┤
│  domain/                                 │
│    - entities.py (Core Models)           │
├─────────────────────────────────────────┤
│  interface_adapters/                     │
│    - parquet_repository.py (Storage)     │
└─────────────────────────────────────────┘
```

### Key Design Patterns

1. **Repository Pattern** - Data access abstraction using Protocol-based interfaces
   - Interface: `application/interfaces.py` (GameRepository Protocol)
   - Implementation: `interface_adapters/parquet_repository.py`
   - Currently stubbed (TODO: implement Parquet persistence)

2. **Service Layer** - Business logic orchestration
   - `GameService` in `application/services.py`
   - Uses dependency injection for repositories
   - Orchestrates demo parsing and metric calculation

3. **Pure Functions** - Metric calculations are stateless functions
   - Located in `application/metrics.py` (508 lines)
   - Take Demo object as input, return float metrics
   - No side effects (except data processing)

### Data Flow Pipeline
```
.dem file → GameService.process_game()
          ↓
    awpy.Demo.parse()
          ↓
    Demo object (with ticks, events, rounds DataFrames)
          ↓
    Metric calculation functions
          ↓
    Numeric results (float)
```

## Domain Models

**Key Entities** (in `domain/entities.py`):
- `Player` - steam_id, name, team, position
- `Team` - name, players
- `Round` - round_number, winner, events, positions
- `Game` - map_name, teams, rounds (aggregate root)

**Demo Object** (from awpy library):
- `demo.ticks` - DataFrame with tick-level player positions (X, Y, Z coordinates)
- `demo.events` - Dict of event DataFrames (bomb_planted, player_death, etc.)
- `demo.rounds` - DataFrame with round metadata (freeze_end, winner_side, etc.)
- `demo.tickrate` - Server tickrate (64 or 128)
- `demo.t_spawn / demo.ct_spawn` - Spawn locations
- `demo.bombsite_locations` - Dict with A/B site coordinates

## Metrics Implementation

The project implements **11 strategic metrics** across 4 categories:

### 1. Pacing Metrics (Tempo)
- `calculate_ttfk()` - Time To First Kill
- `calculate_time_to_bomb_plant()` - Bomb plant timing
- `calculate_average_death_timestamp()` - Average death time

### 2. Aggression Metrics
- `calculate_t_side_avg_dist_to_bombsite()` - T-side positioning
- `calculate_ct_side_forward_presence_count()` - CT aggression
- `calculate_player_spacing()` - Team spread

### 3. Rotational Efficiency
- `calculate_rotation_timing()` - Rotation speed
- `calculate_rotation_success_rate()` - Rotation survival rate
- `calculate_engagement_success_on_rotation()` - Combat effectiveness

### 4. Execute/Attack Metrics
- `calculate_round_win_percentage()` - Post-plant win rate
- `calculate_entry_success_rate()` - Entry fragger success
- `calculate_trade_efficiency()` - Trade kill ratio

### Metric Function Pattern
All metrics follow this structure:
```python
def calculate_metric(demo, ...) -> float:
    if demo is None:
        return 0.0

    # Extract DataFrames
    ticks = demo.ticks
    rounds = demo.rounds

    # Filter and aggregate using Polars
    results = []
    for round in rounds.iter_rows(named=True):
        # Process round data
        results.append(value)

    # Return aggregated metric
    return sum(results) / len(results) if results else 0.0
```

## Technology Stack

- **pandas (>=2.3.3)** - General data manipulation
- **pyarrow (>=21.0.0)** - Parquet file I/O support
- **matplotlib (>=3.10.6)** - Visualization (future use)
- **seaborn (>=0.13.2)** - Statistical plots
- **awpy (>=2.0.2)** - CS2 demo file parsing
- **polars** - High-performance DataFrames (used in metrics via awpy)
- **pytest (>=8.4.2)** - Testing framework

## Testing Guidelines

### Test Structure
- All tests in `tests/` directory
- One test file per metric category
- Each metric has 2 tests: null case (returns 0.0) and valid data case

### Mock Pattern
Tests use mock Demo objects constructed with Polars DataFrames:
```python
@dataclass
class MockDemo:
    ticks: pl.DataFrame
    rounds: pl.DataFrame
    tickrate: int
    t_spawn: dict
    ct_spawn: dict
    bombsite_locations: dict
```

### Test Example
```python
def test_calculate_player_spacing():
    ticks = pl.DataFrame({
        "round_num": [1, 1, 1],
        "tick": [100, 100, 100],
        "side": ["t", "t", "t"],
        "X": [0, 3, 6],
        "Y": [0, 0, 0],
        "Z": [0, 0, 0]
    })

    demo = MockDemo(ticks=ticks, ...)
    result = calculate_player_spacing(demo, 't')

    # Manually calculated expected value
    assert result == 4.0
```

## Current Implementation Status

### Completed
- ✅ Core architecture and layering
- ✅ Domain entities defined
- ✅ 11 metric calculations implemented
- ✅ Repository interface abstraction
- ✅ Comprehensive test suite
- ✅ Demo parsing integration (awpy)

### TODO (Not Yet Implemented)
- ⚠️ **Repository persistence** - Parquet save/load logic in `parquet_repository.py`
- ⚠️ **Game entity population** - Transform Demo data into Game entities (`services.py:21`)
- ⚠️ Full Game entity serialization workflow

### TODOs in Code
```
src/cs2_analyzer/application/services.py:21
  # TODO: Transform the parsed data into a Game entity

src/cs2_analyzer/interface_adapters/parquet_repository.py
  # TODO: Implement Parquet saving logic
  # TODO: Implement Parquet loading logic
```

## Development Principles (from REQUIREMENTS.md)

### Data Storage
- Use **Apache Parquet** columnar format for OLAP workloads
- Implement **partitioning** by frequently-filtered attributes
- Leverage **indexing** (ColumnIndex, OffsetIndex, Bloom Filters)
- Use **predicate pushdown** for efficient queries

### Code Quality
- **SOLID Principles** - Especially Dependency Inversion (abstractions over concrete classes)
- **Single Responsibility** - Each module has one reason to change
- **Cyclomatic Complexity** - Target <10 per class, max 20
- **Unit Testing** - Mock dependencies, test each layer in isolation

### Architecture Rules
- **Dependency Rule** - Source code dependencies point inward toward domain
- External changes (database, UI) cannot affect core business logic
- High-level policies are independent of low-level details

## Working with This Codebase

### Adding a New Metric
1. Define the function in `application/metrics.py`
2. Follow the established pattern (returns 0.0 for null input)
3. Use Polars DataFrames from Demo object
4. Create helper functions if needed (like `euclidean_distance`)
5. Add unit tests in `tests/test_<category>.py`

### Modifying Architecture
- Repository changes: Update Protocol in `interfaces.py` first
- Service changes: Ensure dependencies are injected
- Entity changes: Update `entities.py` dataclasses
- Always maintain layer independence

### Running Analysis
The current workflow:
1. User provides .dem file path
2. `GameService` parses with awpy
3. Repository saves Game entity (currently stub)
4. Returns Demo object to `main.py`
5. `main.py` calls metric functions directly
6. Results printed to console

### Important Notes
- **awpy library** provides the Demo object structure - do not modify
- **Polars** is used in metrics for performance (via awpy)
- **Protocol** (not ABC) is used for interfaces (structural typing)
- Test with **mock DataFrames** - no database mocking needed
