## Feature Metrics and Development Requirements

### I. Strategic Frameworks and Macro-Level Patterns

These metrics are fundamental to identifying an opponent's overall strategic identity (archetype) and rotational discipline, typically relying on **tick-level positional data**.

| Metric Category | Specific Metrics | Definition/Requirements for Development |
| :--- | :--- | :--- |
| **Pacing Metrics (Tempo)** | **Time to First Kill (TTFK)** | The time (in seconds) from the round start to the first `player_death` event. |
| | **Time to Bomb Plant** | The time (in seconds) taken for the `bomb_planted` event on the Terrorist (T) side. |
| | **Average Death Timestamp** | The average time remaining on the round timer across all `player_death` events. |
| **Aggression Metrics** | **T-Side Average Distance to Bombsite** | The average distance of all living T players to the nearest bombsite during the first 30 seconds of the round. A lower distance suggests a faster push. |
| | **CT-Side Forward Presence Count** | The number of Counter-Terrorist (CT) players who cross pre-defined map chokepoints within the first 30 seconds. This requires **pre-annotated map zone data**. |
| | **Player Spacing** | The average distance between all pairs of living teammates throughout the round, measured using full positional data (x, y, z coordinates). |
| **Rotational Efficiency** | **Rotation Timing** | The average time (in seconds) it takes a specific player (the rotator) to travel a common rotational path (e.g., A-to-B) in response to a defined trigger event (e.g., a specific smoke detonation). |
| | **Rotation Success Rate** | The percentage of rounds won when the identified rotator initiates their rotation. |
| | **Engagement Success on Rotation** | Measures if the rotator secured a trade kill or an assist upon reaching the rotational target area. |

### II. Tactical Execution and Round-Phase Analysis

This section focuses on quantifying execution quality for planned attacks (executes) and high-stakes scenarios (retakes/post-plants).

| Metric Category | Specific Metrics | Definition/Requirements for Development |
| :--- | :--- | :--- |
| **T-Side Execute Effectiveness** | **Round Win Percentage** | The frequency with which a specific, classified set execute (identified by a burst of 3+ utility grenades towards a single bombsite within a 5-7 second window) leads to a round win. |
| | **Entry Success Rate** | The success rate of the first player entering the site during the execute (i.e., percentage where the entry fragger secures the opening kill). |
| | **Trade Efficiency** | The frequency with which the entry fragger’s death is immediately traded by a teammate. Requires modeling of **dynamic event dependencies** to identify precise points of failure in complex execution patterns. |
| **CT-Side Defensive Setups** | **Positional Heatmaps** | Visualizations showing the most frequently occupied player locations during the initial 45–60 seconds of CT buy rounds. |
| | **Crossfire Density/Structure** | A quantitative metric derived from **Graph Theory** analysis that measures when and where multiple CT players have intersecting lines of sight over a critical chokepoint. Requires player position and view-angle vector data. |
| **Post-Plant & Retake Efficiency** | **Base Conversion/Success Rates** | Overall T-side post-plant conversion rate and overall CT-side retake success rate. |
| | **Predictive Retake Factors** | Features required to train a Decision Tree or Logistic Regression model: <br> - `player_advantage` (manpower difference). <br> - `time_remaining` (seconds left on bomb timer). <br> - `total_ct_utility_value` (composite score of available CT utility). |

### III. Utility Orchestration and Efficiency

These metrics quantify the tangible impact of utility (grenades) beyond simple usage counts.

| Metric Category | Specific Metrics | Definition/Requirements for Development |
| :--- | :--- | :--- |
| **Flashbang Effectiveness** | **Total Enemy Blind Time (s)** | The sum of seconds that all enemy players were fully blinded by a single flashbang. |
| | **Flash Assists (FA)** | The number of kills secured by a teammate on an enemy within a short time window (e.g., 3 seconds) after that enemy was blinded by the player's flashbang. |
| **Molotov/Incendiary Effectiveness** | **Utility Damage (UD)** | The total amount of health damage dealt to opponents by the fire. |
| | **Position Denial Score** | Measures if a player occupying a common defensive spot (e.g., behind "Quad") was forced to move within 2 seconds of the molotov fire reaching their location. |
| **Composite Score** | **Utility Value Score** | A composite score (e.g., normalized and weighted combination) of metrics like Flash Assists per round, Utility Damage per round, and Total Enemy Blind Time per round. The weights can be determined via regression modeling or coach input. |

### IV. Core Development Requirements

The design and implementation of the application must follow strict software and data management principles to ensure modifiability and performance.

#### 1. Data Processing and Storage Pipeline
*   **Data Ingestion:** The application must parse raw demo files (e.g., `.dem` files) using specialized libraries (e.g., `awpy` or `demoparser2`) to convert them into **structured, queryable data formats**, such as Pandas DataFrames, which provide tick-level granularity (movement, weapon fire, grenade trajectories).
*   **Data Manipulation and Preprocessing:** Utilize the **Pandas** library for cleaning, transforming (e.g., feature engineering), and manipulating the tabular data. Ensure features like feature selection or feature reduction are planned.
*   **Storage Format:** For storing processed data and analysis results, adopt a **columnar storage format** such as **Apache Parquet**. This format is optimized for Online Analytical Processing (OLAP) queries, which involve complex analytical reads.
*   **Query Optimization:** Implement techniques to ensure fast visualization and query speeds:
    *   **Partitioning:** Partition datasets by attributes frequently used for filtering (e.g., date, region, or high-cardinality fields) to enable partition pruning.
    *   **Indexing:** Leverage **advanced indexing** features available in columnar formats, such as **ColumnIndex**, **OffsetIndex**, and **Bloom Filters**, to skip irrelevant data reading and dramatically reduce file I/O time.
    *   **Predicates:** Ensure the analytics engine utilizes **predicate pushdown** (filtering data at the storage level).
*   **Visualization Tools:** Integrate mature Python visualization libraries like **Matplotlib** and **Seaborn** for displaying trends and insights.

#### 2. Software Architecture and Code Quality
*   **Architectural Model:** Adopt a layered approach, such as **Clean Architecture**, to separate concerns. Key layers include:
    *   **Domain:** Encapsulates the core business logic (entities and high-level rules).
    *   **Application:** Contains application-specific business rules and use cases, orchestrating the flow of data.
    *   **Interface Adapters (Presentation/API):** Converts data formats between the internal layers and external agencies (like the database or UI).
*   **Dependency Rule:** Strictly enforce the rule that **source code dependencies must point inwards** toward the core business logic, preventing changes in external details (like the database framework) from affecting core use cases. This means high-level policies are independent of low-level details.
*   **SOLID Principles:** Implement the application following SOLID principles to ensure robustness, flexibility, and maintainability:
    *   **Single Responsibility Principle (SRP):** Each class/module should have only one reason to change.
    *   **Open/Closed Principle (OCP):** Software entities should be **open for extension but closed for modification**.
    *   **Dependency Inversion Principle (DIP):** Rely on **abstractions/interfaces** (e.g., using a Repository interface) rather than concrete implementations to reduce coupling.
*   **Testing:** Implement a rigorous testing strategy, including:
    *   **Unit Testing:** Write unit tests for each layer (Domain, Application, Interface Adapters). Dependencies must be **mocked** to ensure testing is isolated to the component being verified.
    *   **Metrics:** Use **cyclomatic complexity** as a metric to measure code complexity, aiming for a value less than 10 per class (and in any case, not exceeding 20) to ensure high modifiability.

#### 3. MLOps Principles (If Predictive Modeling is Used)
*   **Versioning:** Implement **data versioning** to create a unique reference for the input collection of data (e.g., using an ID or datetime identifier). This is crucial for **reproducibility**—allowing analysis queries to run over the data exactly as it was when a specific result (or error) first occurred.
*   **Reproducibility:** Ensure reproducibility of the analysis workflow by using software versioning (containerization is recommended for deployment) and version control for feature engineering code.
*   **Monitoring:** If models are deployed (even locally), plan for **continuous monitoring** to track metrics like data distribution changes (data drift) and feature creation stability. Monitoring feature data helps assess if the model is operating under familiar conditions, especially if immediate ground truth labels are unavailable.