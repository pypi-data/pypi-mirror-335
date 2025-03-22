# pybrams

**pybrams** is a Python package that allows you to access information and data from the BRAMS (Belgian RAdio Meteor Stations) project. BRAMS is a network of radar receiving stations that use forward scattering techniques to study the meteoroid population. This project, coordinated by the Belgian Institute for Space Aeronomy (BIRA-IASB), provides a valuable source of data for space operators, research scientists and amateur astronomers.

## Features

- Fetch detailed information about BRAMS stations, including their location, name, number of antennas, and more.
- Retrieve raw data files in WAV format, which can be used for in-depth analysis of meteoroid activity.
- Access PNG images representing spectrograms, making it easy to visualize meteoroid detections.
- Compute trajectories, speeds and their associated uncertainties.
- Allow validation of results with optical data.

## Notebooks

This repository includes two key Jupyter notebooks that showcase the usage of **pybrams**:

1. **Reconstruct Trajectory Notebook** ([reconstruct_trajectory.ipynb](./scripts/reconstruct_trajectory.ipynb)):
   - Focuses on reconstructing meteor trajectories from observational radar data.
   - Compares the results with optical data from CAMS-BeNeLux.

2. **MCMC Trajectory Notebook** ([mcmc_trajectory.ipynb](./scripts/mcmc_trajectory.ipynb)):
   - Implements a Markov Chain Monte Carlo (MCMC) method to estimate trajectories uncertainties, based on [Kastinen and Kero (2022)](https://academic.oup.com/mnras/article/517/3/3974/6726639).
   - Provides vizualization plots of the posterior distributions.



These notebooks serve as practical examples and learning tools for analyzing BRAMS data.

## Installation

You can install **pybrams** using pip:

```bash
pip install pybrams
```

## Contributing

Contributions and feedback are welcome! If you'd like to improve this package or report issues, please visit our GitHub repository.

## License

This package is licensed under the MIT License. Feel free to use and modify it as needed.
