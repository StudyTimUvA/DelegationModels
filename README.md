# Delegation Models

This project explores and implements various models of delegation, focusing on the representation, storage, and evaluation of delegation paths and evidence.

## Structure

- **src/models/**: Core models and logic for delegation, evidence, and services.
- **src/tests/**: The test suite.

## Usage

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the main application or tests as needed (from the src directory):

   ```bash
   python3 main.py
   ```

3. (Optional) Run the gen_performance_ployt script to visualize the generated performance values into a graph:

   ```bash
   python3 gen_performance_plot.py
   ```

## Adding new models

To add new models, create a folder in **src/models** and import the base service and database. Implement your model's logic by extending or composing the base classes as needed. To test your model, extend the main code in **src/main.py**.
