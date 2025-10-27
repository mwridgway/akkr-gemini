# CS2 Demo Analyzer

This project analyzes Counter-Strike 2 demo files to extract game data and calculate metrics.

## Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management.

1.  **Install Poetry:**

    Follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation) to install it on your system.

2.  **Install Dependencies:**

    Navigate to the project's root directory and run the following command to install the required dependencies:

    ```bash
    poetry install
    ```

## Usage

To analyze a demo file, run the `main.py` script from within the poetry environment, providing the path to your demo file as an argument.

```bash
poetry run python -m src.cs2_analyzer.main path/to/your/demo.dem
```

Replace `path/to/your/demo.dem` with the actual path to the `.dem` file you want to analyze.