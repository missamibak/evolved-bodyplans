# Thesis excerpt

Text below is reproduced from the author's own 2013 MSc thesis. No figures,
diagrams, or third-party material are included here -- see `IP_STATUS.md` for
why. For the full thesis, contact the author or check the University of East
London's institutional repository once deposited there.

**Neural Self-Organising Maps and Genetic Algorithm: Evolving 3D Cellular
Automata Architectural Model**

Amiina Bakunowicz, MSc Thesis, School of Architecture, Computing and
Engineering, University of East London, September 2013.

## Abstract

Since the dawn of Computer Aided Design, architects have produced digitally
modelled projects that were radical but impossible to build. As fabrication
techniques developed, many such designs materialised, and architects began
using computational methods to re-evaluate designs -- often narrowly, toward
economic and performance-oriented ends, leaving alternative computational
approaches to architectural morphogenesis underexplored.

This thesis proposes a possible solution to the form-finding challenge in a
given architectural context by scripting: a design process built on code that
combines a Genetic Algorithm (GA) and a Self-Organising Map (SOM) to evolve a
predetermined Cellular Automata (CA) model. A computer forms a team with an
architect to develop a design, where the solution is formed gradually during
the running of the algorithm. Designer and machine work through the design
procedure together -- from initial appraisal and concept finalisation through
to basic mass study -- until both are satisfied with the outcome. The
resulting model is then returned to the architect for final adjustment and
detailing.

The proposed algorithm has two tasks. First, based on the information
available after the initial design stages, it develops a schematic body-plan
of the architectural model and parameterises it. Second, applying principles
of natural evolution and biological neural networks, it uses the GA and SOM
together to evolve solutions.

The thesis concentrates mainly on the second stage, where self-organising
mapping is applied to each generation of the evolving body-plan in order to
widen, classify, structure, and exploit the GA's search space. The aim is to
test whether SOM can help speed up the search for a fit solution and avoid
premature convergence, while amplifying the designer's synthetic intuition.
Related theoretical questions are also considered, including the paradox of
expanded choice, coding versus traditional design methods, and the challenge
of evaluating aesthetics computationally.

## Architectural scenario

The task set for the algorithm is to give shape to a building according to a
predetermined functional and spatial arrangement, such that the required
layout stays intact while form emerges from the interactions between the
building's constituent parts. To keep the problem tractable, a single-family
house with three functional areas -- living, working, and resting -- was
chosen as the test case.

## Method, in brief

A Cellular Automata grid represents the building, with each cell assigned one
of the three functional states. A Genetic Algorithm parameterises and evolves
the sizes and positions of the cells across generations, using fitness
criteria built from intersection, neighbour proximity, and golden-ratio
proportion. Because a plain GA narrows its search space too aggressively and
tends to converge on local optima, a Kohonen Self-Organising Map is trained on
each generation to expand, classify, and cluster the space of candidate
solutions before the next round of selection.

The designer stays in the loop throughout. Because the design's fitness is
necessarily multi-criteria and not absolute, the algorithm's stopping
condition is deliberately "fit enough and acceptable to the eye," not
"fittest."

## Advantages and disadvantages of the combined GA-SOM approach

**Advantages**

- Gives the designer visual feedback on the range of possible solutions
- Maps the search space using both the fitness criteria and the evolution of
  the neurons' vectors
- Restructures and expands the space of possibilities rather than narrowing it
- Performs better at generating unexpected solutions
- Introduces a clustering property to the GA's search space
- Maintains the topology of the data space via the neighbourhood function
- Allows evaluation of solutions in non-procedural ways
- Needs fewer generations to reach satisfying results than a classic GA
- Handles models of large dimensionality
- Mitigates several drawbacks of traditional GAs: inaccurate intensification,
  genetic drift, wasted computation, high convergence rate, limited
  diversity, and local optima

**Disadvantages**

- Only reaches full effectiveness with larger populations and neural maps,
  which costs computational power and time
- Combines many interacting parameters -- fitness factor, mutation rate,
  selection rate, convergence rate, winner strength -- making the right
  equilibrium hard to find for a given design problem
- Still carries the underlying challenge of expanded choice and the
  evaluation of aesthetics

## Note on the accompanying code

The Python scripts in this repository are the implementation referred to
above. Stage 1 (`..._boxes only.py`) is the classic-GA stage described in
section 4.2; Stage 2 introduces the SOM. See `README.md` for how the two
stages fit together, and `PATCH_STATUS.md` for the 2026 fixes applied to
Stage 1.
