# Forest Management System

## Installation Instructions

### Environment Preparation

It is recommended to use Python version 3.8 or above.

### Install Dependencies

Execute the following command in the project root directory:

```bash
pip install -r forest_management/requirements.txt
```

### Run the System

#### Run the Main Program

```bash
python forest_management/main.py
```

#### Run the Dash Web Application

```bash
python forest_management/dashboard/app.py
```

Open your browser and visit [http://127.0.0.1:8050/](http://127.0.0.1:8050/) to access the system interface.  
*Note: If the link does not work, please check the validity of the URL and ensure that the server is running. You may also need to refresh the page or try accessing it again.*

### Usage

After entering the system, follow the on-screen prompts to perform operations such as tree management, path management, disease simulation, pathfinding, and conservation area identification.  
The system supports data import/export and statistical analysis. For specific operations, refer to the button and input field descriptions on the interface.

### Required Libraries

- dash
- dash-bootstrap-components
- pandas
- numpy
- networkx
- plotly
- pytest  
(For details, see `forest_management/requirements.txt`)

## Requirements Analysis

### Target Users

- Forestry managers
- Ecological researchers
- Urban planners
- Educators

### Core Requirements

- Visualize forest structure to intuitively display the relationship between trees and paths.
- Support CRUD operations for trees and paths.
- Simulate disease spread to assist in control decision-making.
- Find the shortest path to optimize patrol and transportation routes.
- Automatically identify healthy conservation areas.
- Real-time statistical analysis to monitor forest health status.
- Data import/export for convenient data management and migration.

## System Overview

### Project Name

Forest Management System - An Interactive Forest Management Platform Based on Dash

### Project Description

This is an interactive web application for managing forest ecosystems. It supports users in managing tree nodes and path connections visually and provides advanced features such as disease spread simulation, shortest pathfinding, and conservation area identification. The system uses a graphical interface to provide intuitive tools for monitoring and managing forest conditions.

### Project Background

Managing forest ecosystems requires a comprehensive consideration of tree health status, spatial distribution, and disease spread. Traditional manual management methods are inefficient and prone to errors. This system provides forestry managers with visualized forest structure display, intelligent disease spread simulation, efficient path planning tools, automatic conservation area identification, and real-time statistical analysis through digital means.

### Practical Application Scenarios

- **Forestry Management**: Helps forestry workers monitor forest health and develop protection strategies.
- **Disease Control**: Simulates disease spread paths to develop preventive measures in advance.
- **Ecological Research**: Provides forest structure analysis tools for ecologists.
- **Educational Demonstration**: Serves as a teaching case for graph theory algorithms and data structures.
- **Urban Planning**: Assists in urban greening planning and tree layout design.

### Core Design Concept

The system uses graph theory as the core data structure, abstracting the forest into an undirected weighted graph that includes nodes (trees), edges (paths), and the graph (forest structure). This design allows the system to efficiently handle functions such as disease spread simulation, shortest pathfinding, connected component analysis, and statistical analysis.

## Overall Structure

### Directory Structure

```
forest_management/
├── core/                           # Core data structures and classes
│   ├── __init__.py
│   ├── forest_graph.py             # Forest graph data structure
│   ├── tree_node.py                # Tree node class
│   └── tree_path.py                # Path connection class
├── dashboard/                      # Dash Web application
│   ├── __init__.py
│   ├── app.py                      # Main application entry
│   ├── assets/                     # Static resources
│   │   └── style.css               # Style file
│   ├── callbacks.py                # Callback functions
│   ├── layout.py                   # Page layout
│   └── utils.py                    # Utility functions
├── tasks/                          # Core functional modules
│   ├── __init__.py
│   ├── conservation_areas.py       # Conservation area identification
│   ├── extra_features.py           # Additional features
│   ├── infection_spread.py         # Disease spread simulation
│   └── path_finding.py             # Shortest pathfinding
├── utils/                          # Utility module
│   ├── __init__.py
│   └── data_loader.py              # Data loader
├── visualization/                  # Visualization module
│   ├── __init__.py
│   └── interactive_visualize.py    # Interactive visualization
├── main.py                         # Program entry
├── requirements.txt                # Dependency package list
└── README.md                       # Project description file
tests/                          # Test code
│   ├── __init__.py
│   ├── test_conservation_areas.py
│   ├── test_forest_graph.py
│   ├── test_infection_spread.py
│   ├── test_load_forest_data.py
│   └── test_path_finding.py
```

## Design

### System Architecture

- **Backend**: Implemented in Python with a core data structure of an adjacency list-based undirected weighted graph.
- **Frontend**: Built using Dash for an interactive web interface.
- **Visualization**: Uses Plotly for dynamic display of forest structure and algorithm processes.

### Main Modules and Components

#### Core Data Structures (`core/`)

- **ForestGraph**: The forest graph data structure, using an adjacency list to store the graph structure, supports efficient traversal and querying.
- **TreeNode**: The tree node class, encapsulating tree attributes such as ID, species, age, and health status.
- **TreePath**: The path connection class, representing an undirected weighted edge, supports bidirectional traversal.

#### Functional Modules (`tasks/`)

- **infection_spread.py**: Disease spread simulation, based on a variant of Dijkstra's algorithm.
- **path_finding.py**: Shortest pathfinding, implementing the classic Dijkstra's algorithm.
- **conservation_areas.py**: Conservation area identification, based on depth-first search (DFS) to find connected components.
- **extra_features.py**: Provides statistical analysis features, such as health status statistics and tree species distribution.

#### Web Application (`dashboard/`)

- **app.py**: The main entry for the Dash application, initializes the application and registers callbacks.
- **layout.py**: Defines the user interface layout, including various input controls and display areas.
- **callbacks.py**: Handles user interactions through callback functions, implementing various functional logics.

#### Visualization (`visualization/`)

- **interactive_visualize.py**: Generates an interactive forest graph, supporting node highlighting and path display.

## Data Structures

### ForestGraph

- **Design Concept**: Uses an adjacency list to store the graph structure, with each node storing a list of all adjacent edges.
- **Advantages**: High space efficiency, suitable for sparse graphs; fast traversal of adjacent nodes.
- **Time Complexity**:
  - Adding/Removing nodes: O(1)
  - Adding/Removing edges: O(1)
  - Traversing adjacent nodes: O(degree)

### TreeNode

- **Design Concept**: Encapsulates all attributes of a tree, implementing hash and comparison operations.
- **Hash Implementation**: Based on `tree_id` to ensure uniqueness within the graph.
- **Health Status**: Uses an enumeration type to ensure consistency of status values.

### TreePath

- **Design Concept**: Represents an undirected weighted edge, supporting bidirectional traversal.
- **Hash Implementation**: Based on an unordered set of node IDs, ensuring edge uniqueness.
- **Weight**: The distance value is used for shortest path calculation and disease spread simulation.

## Algorithm Explanation

### Disease Spread Simulation

- **Algorithm Principle**: Based on a variant of Dijkstra's algorithm, considering spread speed and time.
- **Input Parameters**: Starting infected tree, spread speed.
- **Output Results**: Infection time and order for each tree.
- **Application Scenario**: Predicting disease spread paths to develop control strategies.
- **Example Scenario**: Using a variant of Dijkstra's algorithm, each tree is considered a node in the graph, with path lengths as weights. Starting from the infection source, the system simulates the spread of disease to other trees in the shortest time possible, calculating the earliest infection time for each tree.  
  *Example*: Suppose there are 10 trees in the forest, connected by paths. Tree 1 is initially infected, with a spread speed of 2 meters per day. The system automatically calculates the infection time for each tree and dynamically displays the spread process on the interface. For instance, the infection sequence might be Tree 1 → Tree 3 → Tree 5, with the final display showing the infection order and time for all trees.

### Shortest Pathfinding

- **Algorithm Principle**: Classic Dijkstra's algorithm, optimized with a priority queue.
- **Input Parameters**: Starting tree, target tree.
- **Output Results**: Shortest path node sequence and total distance.
- **Application Scenario**: Planning patrol routes, calculating transportation distances.
- **Example Scenario**: Using the classic Dijkstra's algorithm, the system uses a priority queue to expand from the starting tree to the target tree, finding the shortest path node sequence.  
  *Example*: A forestry patrol officer needs to inspect from Tree 2 to Tree 8. By inputting the starting tree ID as 2 and the target tree ID as 8, the system automatically calculates and highlights the shortest patrol path (e.g., 2 → 4 → 6 → 8) and displays the total distance.

### Conservation Area Identification

- **Algorithm Principle**: Depth-first search (DFS) to find connected components.
- **Input Parameters**: Minimum conservation area size.
- **Output Results**: List of all healthy tree conservation areas.
- **Application Scenario**: Identifying forest areas that need focused protection.
- **Example Scenario**: Using the DFS algorithm, the system traverses all healthy tree nodes to find all connected healthy areas (connected components) and filters out those that meet the minimum size requirement for conservation areas.  
  *Example*: There are multiple healthy tree areas in the forest. After clicking "Highlight Conservation Area," the system automatically identifies and highlights the largest connected healthy area. For instance, Trees 3, 4, and 7 form a conservation area, which is marked with a different color on the interface, along with the number of trees in the conservation area.

## Evolution of Data Structures

### 1. Data Structure Architecture Refactoring - From Separated to Adjacency List

#### Original Version (Separated Storage):

```python
class ForestGraph:
    def __init__(self):
        self.nodes = set()  # Stores all tree nodes
        self.edges = set()  # Stores all paths
```

**Problems**:
- Low efficiency for querying adjacent nodes, requiring traversal of all edges.
- Dispersed data structure, complex logic.
- Not suitable for direct application of graph algorithms.

#### Current Version (Adjacency List Storage):

```python
class ForestGraph:
    def __init__(self):
        self.adjacency = defaultdict(list)
```

**Performance Comparison**:

| Operation          | Original Version Complexity | Current Version Complexity | Performance Improvement |
|--------------------|-----------------------------|----------------------------|-------------------------|
| Adjacent Query     | O(E)                        | O(degree)                  | Significant improvement |
| Disease Spread     | O(V × E)                    | O((V + E) log V)           | Significant improvement |
| Shortest Path      | O(V² + E)                   | O((V + E) log V)           | Significant improvement |

**Reasons for Change**:

- **Improved Efficiency**: The separated structure typically stores nodes and edges separately. Querying all adjacent nodes for a particular node requires traversing all edges, which is inefficient. The adjacency list directly stores adjacent nodes together, making lookup and traversal faster.
- **Simplified Operations**: The adjacency list structure makes adding, deleting nodes or edges more intuitive and efficient, with simpler code implementation.
- **Space Savings**: For sparse graphs (most forest management scenarios are sparse graphs), the adjacency list is more memory-efficient than adjacency matrix structures.
- **Ease of Extension**: The adjacency list structure is easier to extend with new functionalities, such as pathfinding and infection spread simulation algorithms.

**Effects of Changes**:

- **Faster Graph Algorithm Execution**: Algorithms like BFS, DFS, shortest path, and connected components run more efficiently with the adjacency list structure.
- **Improved Code Maintainability**: The structure is clearer, making it easier for subsequent development and maintenance.
- **Better Alignment with Business Needs**: In the forest management system, the connections between trees naturally fit the adjacency list representation, facilitating the simulation of mutual influences between trees in the forest.

### 2. Hash Function Design Optimization

#### Original Version:

```python
def __hash__(self):
    return hash((self.tree_id, self.species, self.age, self.health_status))
```

**Problems**:
- High hash calculation complexity involving multiple fields.
- Complex comparison operations with low performance.

#### Current Version:

```python
def __hash__(self):
    return hash(self.tree_id)
```

**Performance Comparison**:

| Operation          | Original Version Complexity | Current Version Complexity | Performance Improvement |
|--------------------|-----------------------------|----------------------------|-------------------------|
| Hash Calculation   | Multi-field hash            | Single-field hash          | Significant improvement |
| Object Comparison  | Multi-field comparison      | Single-field comparison    | Significant improvement |

### 3. Edge Object Design Optimization

#### Original Version:

```python
def __hash__(self):
    return hash((self.tree1.tree_id, self.tree2.tree_id))
```

**Problems**:
- Complex handling of undirected edges, requiring manual order management.
- Insufficient integrity checks for edges.

#### Current Version:

```python
def __hash__(self):
    return hash(frozenset({self.tree1.tree_id, self.tree2.tree_id}))
```

**Performance Comparison**:

| Operation                  | Original Version Complexity | Current Version Complexity | Performance Improvement |
|----------------------------|-----------------------------|----------------------------|-------------------------|
| Undirected Edge Handling   | Manual order management     | Automatic handling with frozenset | Code more concise       |
| Edge Integrity Check       | Node check only             | Distance check included    | More accurate           |

## Functional Demonstration

### Interface Explanation

- **Operation Area**: All functions have input boxes and buttons for intuitive operation.
- **Visualization Area**: Node colors distinguish health/infected/conservation areas, and edge width/color can differentiate path types.
- **Interactivity**: Supports node highlighting, path highlighting, and dynamic updates.
- **Statistics Area**: Pie charts and bar charts display forest health and tree species distribution.

### Basic Functional Operations

#### Tree Management

- **Add Tree**: Input tree ID, species, age, health status, and click "Add Tree".
- **Remove Tree**: Input tree ID and click "Remove Tree".

#### Path Management

- **Add Path**: Input starting tree ID, target tree ID, distance, and click "Add Path".
- **Remove Path**: Input the starting and ending tree IDs of the path and click "Remove Path".

#### Disease Spread Simulation

- Input the starting infected tree ID and spread speed.
- Click "Start Simulation" to begin the simulation, and the system will display the spread process and results.

#### Shortest Pathfinding

- Input the starting tree ID and target tree ID.
- Click "Find Path" to find the shortest path, and the system will highlight the path and display the total distance.

#### Conservation Area Identification

- Click "Highlight Conservation Area", and the system will identify and highlight the largest healthy tree conservation area.

#### Data Import/Export

- **Import Data**: Input the file paths for tree data and path data in CSV format, and click "Import Data".
- **Export Data**: Click "Export Data" to export the current forest data.

#### Statistical Analysis

- Click "Show Statistics" to view forest health status and tree species distribution statistics.

## Testing Methods

### Unit Testing

- **Framework**: pytest
- **Coverage**: Current test coverage reaches 97%, covering core data structure operations, graph algorithm implementations, data loading functions, and web interface callbacks.
- **Performance Testing**: Run performance tests using pytest to ensure algorithm efficiency meets expectations.
- **Test Result Display**:

```
Name                                            Stmts   Miss  Cover
-------------------------------------------------------------------
forest_management/core/__init__.py                  0      0   100%
forest_management/core/forest_graph.py             50      0   100%
forest_management/core/tree_node.py                21      2    90%
forest_management/core/tree_path.py                17      0   100%
forest_management/tasks/__init__.py                 0      0   100%
forest_management/tasks/conservation_areas.py      19      0   100%
forest_management/tasks/infection_spread.py        37      1    97%
forest_management/tasks/path_finding.py            32      2    94%
forest_management/utils/__init__.py                 0      0   100%
forest_management/utils/data_loader.py             33      0   100%
tests/test_conservation_areas.py                   27      1    96%
tests/test_data_loader.py                         125      1    99%
tests/test_forest_graph.py                        121      6    95%
tests/test_infection_spread.py                    146      5    97%
tests/test_load_forest_data.py                     15      2    87%
tests/test_path_finding.py                         25      1    96%
tests/test_tree_path.py                            67      1    99%
-------------------------------------------------------------------
TOTAL                                             735     22    97%
```

## Major Challenges

- **Data Structure Refactoring**: Transitioning from a separated structure to an adjacency list significantly improved algorithm efficiency and code maintainability.
- **Algorithm Optimization**: For sparse graph scenarios, using adjacency lists and priority queues significantly enhanced performance.
- **Interface Interaction**: Dash components and callback logic are complex and require careful design to ensure a smooth user experience.

## Optimization and Learning Experience

- **Code Structure Optimization**: Modular design for easier expansion and maintenance.
- **Integration of Theoretical Algorithms and Business Scenarios**: Enhanced engineering implementation capabilities by deeply integrating theoretical algorithms with practical business needs.
- **Frontend and Backend Collaboration**: Improved full-stack development skills.
- **User Testing**: Continuous optimization of the interface and interaction logic through multiple rounds of user testing.
