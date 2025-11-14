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
   - Fully implemented with normalized 6-table Parquet storage

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
.dem file → AwpyDemoParser.parse()
          ↓
    awpy Demo object (ticks, events, rounds DataFrames)
          ↓
    GameService._build_teams() + _build_rounds()
          ↓
    Game entity (teams, players, rounds with events/positions)
          ↓
    ParquetGameRepository.save()
          ↓
    Normalized Parquet tables (6 files in data/processed/)
          │
          ├─ games.parquet (game metadata)
          ├─ teams.parquet (team info)
          ├─ players.parquet (player info)
          ├─ rounds.parquet (round metadata)
          ├─ events.parquet (all game events)
          └─ positions.parquet (player positions)
          ↓
    Metric calculation functions (use Demo object)
          ↓
    Numeric results (float)
```

**Key Infrastructure Components:**
- **DemoParser** (`application/ingestion.py`) - Abstraction for demo parsing with Protocol-based interface
- **GameService** (`application/services.py`) - Orchestrates parsing and Game entity transformation
- **ParquetGameRepository** (`interface_adapters/parquet_repository.py`) - Normalized storage with 6 tables

## Domain Models

**Key Entities** (in `domain/entities.py`):
- `Player` - steam_id, name, team, position
- `Team` - name, players
- `Round` - round_number, winner, events, positions
- `Game` - map_name, teams, rounds (aggregate root)

**Demo Object** (from awpy library):
- `demo.ticks` - Polars DataFrame with tick-level player positions (X, Y, Z, yaw, pitch)
- `demo.events` - Dict of event Polars DataFrames (bomb_planted, player_death, etc.)
- `demo.rounds` - Polars DataFrame with round metadata (freeze_end, winner_side, etc.)
- `demo.header` - Dict with map_name and other metadata
- `demo.tickrate` - Server tickrate (64 or 128)
- `demo.t_players` / `demo.ct_players` - Lists of player names by team
- `demo.t_spawn` / `demo.ct_spawn` - Spawn locations (dict with X, Y, Z)
- `demo.bombsite_locations` - Dict with A/B site coordinates

## Metrics Implementation

The project implements **12 strategic metrics** across 4 categories:

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
    events: dict  # Dict of event DataFrames
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

### Phase 1: Core Architecture (✅ COMPLETE)
- ✅ DemoParser abstraction with Protocol interface
- ✅ AwpyDemoParser implementation
- ✅ Full Game entity transformation (teams, players, rounds, events, positions)
- ✅ Normalized Parquet storage (6-table schema)
- ✅ ParquetGameRepository with save/load roundtrip
- ✅ Comprehensive test suite (ingestion, transformation, repository)

### Phase 2: Strategic Metrics (✅ COMPLETE)
- ✅ 12 metric calculations implemented
- ✅ Pacing metrics (3): TTFK, Bomb Plant Time, Average Death Timestamp
- ✅ Aggression metrics (3): T-Side Distance, CT Forward Presence, Player Spacing
- ✅ Rotational efficiency (3): Timing, Success Rate, Engagement Success
- ✅ Execute effectiveness (3): Round Win %, Entry Success, Trade Efficiency

### Next Phases
- Phase 3A: CT-Side Defensive Setups (Positional Heatmaps, Crossfire Density)
- Phase 3B: Post-Plant & Retake Efficiency
- Phase 4: Utility Orchestration (Flashbang/Molotov effectiveness)

## Parquet Storage Schema

The repository uses a **normalized 6-table schema** optimized for OLAP workloads:

### Table Structure
```
data/processed/
├── games.parquet          # Game metadata
│   ├── game_id (UUID)
│   ├── map_name
│   ├── timestamp
│   ├── num_teams
│   └── num_rounds
│
├── teams.parquet          # Team information
│   ├── team_id
│   ├── game_id (FK)
│   ├── name
│   └── num_players
│
├── players.parquet        # Player information
│   ├── player_id
│   ├── team_id (FK)
│   ├── game_id (FK)
│   ├── steam_id
│   ├── name
│   └── team (T/CT)
│
├── rounds.parquet         # Round metadata
│   ├── round_id
│   ├── game_id (FK)
│   ├── round_number
│   ├── winner
│   ├── num_events
│   └── num_positions
│
├── events.parquet         # All game events
│   ├── event_id
│   ├── round_id (FK)
│   ├── game_id (FK)
│   ├── tick
│   ├── event_type
│   └── [dynamic event fields]
│
└── positions.parquet      # Player positions (sampled)
    ├── position_id
    ├── round_id (FK)
    ├── game_id (FK)
    ├── tick
    ├── player_steamid
    ├── side (T/CT)
    ├── X, Y, Z
    ├── yaw
    └── pitch
```

### Repository Methods
- `save(game: Game)` - Decomposes Game entity into 6 DataFrames, saves to Parquet
- `get(game_id: str)` - Loads and reconstructs full Game entity from tables
- `_append_to_table()` - Appends to existing Parquet files (concat pattern)
- `_load_table()` - Loads Parquet table with pandas

### Position Sampling
To reduce storage size, positions are sampled every 16 ticks (~0.25s at 64 tick rate).
This is configured in `GameService._extract_round_positions()`.

### Storage Notes
- Sample demo files are available in `data/raw/` (5 Falcons vs Vitality matches)
- Current implementation generates 4 primary tables: games, rounds, events, positions
- Teams and players data are embedded in the games table structure
- Repository supports append-only pattern for multiple games (DataFrame concatenation)

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
2. `GameService` parses with awpy, returns Demo object
3. Repository saves Game entity to normalized Parquet tables in `data/processed/`
4. `main.py` receives Demo object
5. `main.py` calls metric functions directly (metrics operate on Demo object, not Game entity)
6. Results printed to console

### Important Notes
- **awpy library** provides the Demo object structure - do not modify
- **Polars vs Pandas**: Metrics use Polars DataFrames (via awpy Demo object), Repository uses pandas for Parquet I/O
- **Metrics operate on Demo object**, not on the transformed Game entity
- **Protocol** (not ABC) is used for interfaces (structural typing)
- **Helper functions**: `euclidean_distance()` and other utilities are in `metrics.py`
- Test with **mock DataFrames** - no database mocking needed
