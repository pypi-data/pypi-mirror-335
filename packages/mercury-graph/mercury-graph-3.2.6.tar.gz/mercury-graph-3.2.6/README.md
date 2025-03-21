# Mercury Graph

![](https://img.shields.io/pypi/v/mercury-graph?label=latest%20pypi%20build)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-3816/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-3916/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-31011/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3128/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3131/)
[![Apache 2 license](https://shields.io/badge/license-Apache%202-blue)](http://www.apache.org/licenses/LICENSE-2.0)
[![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://github.com/BBVA/mercury-graph/issues)


## What is this?

**`mercury-graph`** is a Python library that offers **graph analytics capabilities with a technology-agnostic API**, enabling users to apply a curated range of performant and scalable algorithms and utilities regardless of the underlying data framework. The consistent, scikit-like interface abstracts away the complexities of internal transformations, allowing users to effortlessly switch between different graph representations to leverage optimized algorithms implemented using pure Python, [**numba**](https://numba.pydata.org/), [**networkx**](https://networkx.org/) and PySpark [**GraphFrames**](https://graphframes.github.io/graphframes/docs/_site/index.html).

![mercury-graph cheatsheet](docs/images/mercury_graph.png)


## Try it without installation in Google Colab

* mercury.graph methods using the [FIFA dataset](https://www.kaggle.com/datasets/artimous/complete-fifa-2017-player-dataset-global) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BBVA/mercury-graph/blob/master/tutorials/mercury-graph-tutorial-fifa.ipynb)

  * Version without Spark [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BBVA/mercury-graph/blob/master/tutorials/mercury-graph-tutorial-fifa-nospark.ipynb)

* mercury.graph methods using the [BankSim dataset](https://www.researchgate.net/publication/265736405_BankSim_A_Bank_Payment_Simulation_for_Fraud_Detection_Research) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BBVA/mercury-graph/blob/master/tutorials/mercury-graph-tutorial-banksim.ipynb)

  * Version without Spark [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BBVA/mercury-graph/blob/master/tutorials/mercury-graph-tutorial-banksim-nospark.ipynb)

* Interactive graph visualization: The Moebius class [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BBVA/mercury-graph/blob/master/tutorials/moebius_demo.ipynb)

* Graph-based feature engineering with mercury.graph [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BBVA/mercury-graph/blob/master/tutorials/mercury-graph-tutorial-graph-features.ipynb)


## Install

```bash
pip install mercury-graph
```


## Documentation

  * HTML documentation: <https://bbva.github.io/mercury-graph/site/>


## Testing

After installation, the test suite can be launched with coverage statistics from outside the source directory (packages `pytest` and `coverage` must be installed):

```bash
./test.sh
```


## License

```text
                         Apache License
                   Version 2.0, January 2004
                http://www.apache.org/licenses/

     Copyright 2021-23, Banco de Bilbao Vizcaya Argentaria, S.A.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0
```


## Contributing

If you can complete a new feature on your own (new feature, doc, tests, version bump, changelog), you can directly create a Pull request to the master branch. Of course, you will get help via the PR.

An easier way to contribute is to create a new issue. If the idea is accepted, we will create a branch for you and start working on how to implement it.


## Help and support

  * [Mercury team](mailto:mercury.team@bbva.com?subject=[mercury-graph])
  * [Issues](https://github.com/BBVA/mercury-graph/issues)


## Mercury project at BBVA

`mercury-graph` is a part of [**`Mercury`**](https://www.bbvaaifactory.com/mercury/), a collaborative library developed by the **Advanced Analytics community at BBVA** that offers a broad range of tools to simplify and accelerate data science workflows. This library was originally an [Inner Source](https://en.wikipedia.org/wiki/Inner_source) project, but some components, like `mercury.graph`, have been released as Open Source.

If you're interested in learning more about the Mercury project, we recommend reading this blog [post](https://www.bbvaaifactory.com/mercury-acelerando-la-reutilizacion-en-ciencia-de-datos-dentro-de-bbva/) from **BBVA AI Factory**.
