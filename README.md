# IT251-DSA-Mini-Project: Register Allocator

## Project Description

The Register Allocator project is a powerful tool designed to optimize register allocation for variables in computer programs. Utilizing graph coloring techniques and implementing Chaitin's Briggs algorithm and Linear Scan, this project aims to reduce register spills to memory and enhance overall program performance.

![colored_int_graph](https://github.com/Vignaraj-pai/Register-Allocation-Visualizer/assets/93054118/b607e0a6-5204-49ec-9d28-6ac02546c653)

## Introduction

Register allocation is a critical aspect of program optimization, managing the allocation of hardware registers efficiently. When the number of variables in a program exceeds the available registers, compilers must decide which variables should reside in registers during execution. This decision significantly impacts program performance and efficiency.

This project employs graph coloring algorithms, representing variable dependencies as a graph, where nodes represent variables and edges represent dependencies. Graph coloring assigns different colors (representing registers) to nodes (variables) to ensure that adjacent nodes do not share the same color. This approach minimizes the need for spilling variables to memory, reducing memory access operations and improving program execution speed.

## Implemented Algorithms

### 1. Chaitin's Briggs Algorithm

Chaitin's Briggs algorithm is a well-known graph coloring algorithm. It prioritizes register allocation based on variable liveness and interference. By considering variable live ranges and minimizing conflicts between them, this algorithm efficiently allocates registers, ensuring optimal performance.

### 2. Linear Scan Algorithm

The Linear Scan algorithm is another implemented approach. It allocates registers by scanning program variables in a specific order, identifying live ranges, and assigning registers accordingly. This linear-time algorithm efficiently utilizes available registers.


## Contributors

- [Vignaraj Pai](https://github.com/Vignaraj-pai)
- [Srinvasa R](https://github.com/Wolfram70)
- [Abhishek Sathpaty](https://github.com/AbhishekSatpathy4848)
- [Sachin Prasanna](https://github.com/sachinprasanna7)
- [Abhayjit Singh Gulati](https://github.com/abhayjit07)


