# Causara

**Support:** [support@causara.com](mailto:support@causara.com)

**Documentation:** https://docs.causara.com

**Website:** https://www.causara.com

Causara is a Python package and GUI that enhances the entire lifecycle of a Gurobi model. We leverage advanced AI to create, adapt, and interact with Gurobi models.

**Key Features:**

*   **Learn from Data:** Generate Gurobi models directly from your data *without* explicitly defining an objective function. Causara can translate data into a fully functional Gurobi model.
*   **Compile Python to Gurobi:**  Write your optimization logic in plain Python and Causara's AI will compile it into an efficient Gurobi model.  No need to grapple with Gurobi's API directly.
*   **AI-Powered GUI:**  Interact with your models through a no-code interface. Use natural language to make adjustments, interpret solutions, and manage your optimization tasks.
*   **Post-Processing:** Refine solutions obtained from Gurobi using custom Python functions to better reflect real-world complexities and constraints.
*   **Fine-Tuning:**  Improve model accuracy by fine-tuning both constant parameters and the model itself using real-world data and performance feedback.
*   **Metrics and Reporting:**  Create custom metrics and utilize AI-generated metrics to summarize and visualize key performance indicators (KPIs) of your solutions.
*   **Custom Scripts:** Integrate external data sources, create custom visualizations, export solutions, and compute real-world objective values using Python scripts (read, view, write, objective).
*   **Cloud Management:**  Upload, download, and manage your models and datasets on the Causara cloud platform.
*   **Detailed Documentation**: Comprehensive API reference and tutorials.


### Installation

Install Causara via pip:

```bash
pip install causara
```


### Creating a TEST-key

```bash
import causara
causara.get_test_key("your_email@example.com")
```


### Quickstart

Below is a brief example of compiling and solving a Traveling Salesman Problem (TSP) model:

```python
from causara import *
import gurobipy as gp
from gurobipy import GRB
import causara
import numpy as np


def tsp(p, c):
    # Identify selected cities based on p["cities"]
    selected_cities = [i for i in range(len(p["cities"])) if p["cities"][i] == 1]
    n = len(selected_cities)

    # Create a new Gurobi model
    model = gp.Model()
    # Create binary variables: route[i, j] == 1 indicates that selected city i is assigned to position j in the route.
    route = model.addVars(n, n, vtype=GRB.BINARY, name='route')

    # Add constraints: each city must be assigned to one unique position, and each position must be filled by one city.
    for i in range(n):
        model.addConstr(gp.quicksum(route[i, j] for j in range(n)) == 1)
        model.addConstr(gp.quicksum(route[j, i] for j in range(n)) == 1)

    # Ensure that city 0 starts the route.
    model.addConstr(route[0, 0] == 1)

    # Define the objective function to minimize the total route length.
    route_length = 0
    for city1 in range(n):
        c1 = selected_cities[city1]
        for pos1 in range(n):
            for city2 in range(n):
                c2 = selected_cities[city2]
                for pos2 in range(n):
                    if pos2 == pos1 + 1:
                        route_length += c["distance"][c1][c2] * route[city1, pos1] * route[city2, pos2]
                    if pos1 == 0 and pos2 == n - 1:
                        route_length += c["distance"][c1][c2] * route[city1, pos2] * route[city2, pos1]
    model.setObjective(route_length, GRB.MINIMIZE)
    return model


# Create a compiled model object with your unique key and model name.
compiledGurobiModel = CompiledGurobiModel(key="your_key", model_name="TSP")

# Compile the TSP model, specifying 'route' as the target variable.
compiledGurobiModel.compile_from_gurobi(tsp, target_vars=["route"], c=causara.Demos.TSP_real_data.c)

# Create a random problem instance
p = {"cities": np.random.choice([0, 1], size=30)}

# Solve the compiled model and select the first solution
x, x_complete, obj_value = compiledGurobiModel.solve(p)[0]

# Display the results.
print(f"x: {x}")
print(f"objective value: {obj_value}")
```

### LICENSE

This project is licensed under the terms provided in LICENSE.txt

