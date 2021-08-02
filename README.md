# Aggregation of Crowdsourced Ontology-Based Item Descriptions by Hierarchical Voting (VLDB Crowd Science Workshop)

## Requirements

The list of required Python packages is provided in `requirements.txt`. It is recommended to use venv: create 
an environment and install packages by running:

    $ pip install -r requirements.txt

## What's inside

`crowd-science-workshop-experiments.py` - experiments for VLDB Crowd Science Workshop 2021 paper.

`aggregation.py` - aggregation algorithms (OntoVoting).

`util.py` - convenience functions for working with ontologies (e.g., finding generalizations).

`create_ontology.py` - the script for ontology generation (the ontologies are places in ontologies folder).

`labeling_generator.py` - Algorithms for generating ground truth and user model.
