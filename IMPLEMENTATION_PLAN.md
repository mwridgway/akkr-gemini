# Implementation Plan: CS2 Analytics Engine

This document outlines the iterative development plan for the CS2 Analytics Engine, as specified in `REQUIREMENTS.md`.

## Phase 1: Project Setup and Core Architecture

**Goal:** Establish the foundational structure of the application, including the directory layout for Clean Architecture, and set up the data processing pipeline.

**Tasks:**

1.  **Scaffold Project Structure:**
    *   Create the directory structure based on Clean Architecture principles:
        ```
        csgo_analyzer/
        ├── src/
        │   └── csgo_analyzer/
        │       ├── domain/
        │       ├── application/
        │       └── interface_adapters/
        └── tests/
        ```
2.  **Initialize Project:**
    *   Use `poetry` to initialize the project and create the `pyproject.toml` file.
3.  **Install Dependencies:**
    *   Add the following dependencies to `pyproject.toml`:
        *   `pandas`
        *   `pyarrow`
        *   `matplotlib`
        *   `seaborn`
        *   `awpy` (for demo parsing)
        *   `pytest` (for testing)
4.  **Data Ingestion Module:**
    *   Create a module within `interface_adapters` to handle the parsing of `.dem` files using `awpy`.
5.  **Domain Entities:**
    *   Define core domain entities (e.g., `Player`, `Team`, `Round`, `Game`) in the `domain` layer.
6.  **Application Services:**
    *   Create application services (use cases) in the `application` layer to orchestrate the data flow.
7.  **Repository Interfaces:**
    *   Define repository interfaces in the `application` layer for data storage and retrieval.
8.  **Parquet Storage Implementation:**
    *   Create a concrete implementation of the repository interfaces in the `interface_adapters` layer to store and retrieve data from Parquet files.
9.  **Basic CLI:**
    *   Create a simple command-line interface to trigger the data processing pipeline.
10. **Unit Tests:**
    *   Set up `pytest` and write initial unit tests for the data ingestion and domain entities.

## Phase 2: Implementation of "Strategic Frameworks and Macro-Level Patterns"

**Goal:** Implement the metrics related to pacing, aggression, and rotational efficiency.

**Tasks:**

1.  **Pacing Metrics:**
    *   Implement the calculation of **Time to First Kill (TTFK)**.
    *   Implement the calculation of **Time to Bomb Plant**.
    *   Implement the calculation of **Average Death Timestamp**.
2.  **Aggression Metrics:**
    *   Implement the calculation of **T-Side Average Distance to Bombsite**.
    *   Implement the calculation of **CT-Side Forward Presence Count**.
    *   Implement the calculation of **Player Spacing**.
3.  **Rotational Efficiency:**
    *   Implement the calculation of **Rotation Timing**.
    *   Implement the calculation of **Rotation Success Rate**.
    *   Implement the calculation of **Engagement Success on Rotation**.
4.  **Visualization:**
    *   Create basic visualizations for these metrics using Matplotlib/Seaborn.
5.  **Testing:**
    *   Write unit tests for each metric calculation.

## Phase 3: Implementation of "Tactical Execution and Round-Phase Analysis"

**Goal:** Implement the metrics related to T-Side execution, CT-Side defensive setups, and post-plant/retake efficiency.

**Tasks:**

1.  **T-Side Execute Effectiveness:**
    *   Implement the calculation of **Round Win Percentage** for set executes.
    *   Implement the calculation of **Entry Success Rate**.
    *   Implement the calculation of **Trade Efficiency**.
2.  **CT-Side Defensive Setups:**
    *   Implement the generation of **Positional Heatmaps**.
    *   Implement the calculation of **Crossfire Density/Structure** (using `networkx`).
3.  **Post-Plant & Retake Efficiency:**
    *   Implement the calculation of **Base Conversion/Success Rates**.
    *   Implement the **Predictive Retake Factors** model (using `scikit-learn`).
4.  **Visualization:**
    *   Create visualizations for these metrics, including heatmaps.
5.  **Testing:**
    *   Write unit tests for each metric calculation and the predictive model.

## Phase 4: Implementation of "Utility Orchestration and Efficiency"

**Goal:** Implement the metrics related to the effectiveness of utility usage.

**Tasks:**

1.  **Flashbang Effectiveness:**
    *   Implement the calculation of **Total Enemy Blind Time**.
    *   Implement the calculation of **Flash Assists (FA)**.
2.  **Molotov/Incendiary Effectiveness:**
    *   Implement the calculation of **Utility Damage (UD)**.
    *   Implement the calculation of **Position Denial Score**.
3.  **Composite Score:**
    *   Implement the calculation of the **Utility Value Score**.
4.  **Visualization:**
    *   Create visualizations for these metrics.
5.  **Testing:**
    *   Write unit tests for each metric calculation.

## Phase 5: Refinement, Documentation, and Deployment Preparation

**Goal:** Refine the application, add comprehensive documentation, and prepare for deployment.

**Tasks:**

1.  **Code Refinement:**
    *   Review and refactor the codebase for clarity, performance, and adherence to SOLID principles.
    *   Measure and reduce cyclomatic complexity.
2.  **Documentation:**
    *   Write comprehensive docstrings for all modules, classes, and functions.
    *   Create a `README.md` file with detailed setup and usage instructions.
3.  **MLOps:**
    *   Implement data versioning.
    *   Containerize the application using Docker.
4.  **Final Testing:**
    *   Perform end-to-end testing of the entire data processing and analysis pipeline.
