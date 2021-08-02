import random
import math

import numpy as np

from owlready2 import get_ontology

import aggregation
import util
import labeling_generator

def process_dataset(dataset, labeler):
    """Labels all items of the dataset with the specified labeler."""
    return {item: labeler.label_object(item, true_description) for item, true_description in dataset.items()}

def process_dataset_random_labelers(dataset, labelers, probs, n_labelers, aggregation_constructor):
    """Labels each item by selecting labelers by random and then aggregating by the specified algorithm."""
    labels = {}
    for item, true_description in dataset.items():
        selected_labelers = random.choices(labelers, weights=probs, k=n_labelers)
        assert(len(selected_labelers) == n_labelers)
        agg = aggregation_constructor(selected_labelers)
        labels[item] = agg.label_object(item, true_description)
    return labels

def evaluate(ground_truth, labels):
    s = 0
    cnt = 0
    for item in sorted(ground_truth.keys()):
        metric_val = util.metric(ground_truth[item], labels[item])
        if metric_val < 10000:
            s += metric_val
            cnt += 1
        else:
            pass
            #print('Warning: metric undefined (one of the descriptions is empty)')
    if cnt > 0:
        return s / len(ground_truth)
    else:
        #print('Warning: metric undefined (one of the descriptions is empty)')
        return math.nan

def label_and_eval(ground_truth, labeler):
    return evaluate(ground_truth, process_dataset(ground_truth, labeler))

def repeated_label_and_eval(ground_truth, labeler, reps):
    vs = []
    for _ in range(reps):
        vs.append(label_and_eval(ground_truth, labeler))
    return (np.nanmean(vs), np.nanstd(vs)) #if vs else (-1.0, -1.0)

def generic_averager(foo, reps):
    """Calls function reps times and calculates statistics on returned values."""
    vs = []
    for _ in range(reps):
        vs.append(foo())
    return (np.nanmean(vs), np.nanstd(vs))

# Load the ontologies
small_onto = get_ontology('ontologies/ontoagg_small.owl').load()
util.print_description(small_onto)
medium_onto = get_ontology('ontologies/ontoagg_medium.owl').load()
util.print_description(medium_onto)
large_onto = get_ontology('ontologies/ontoagg_large.owl').load()
util.print_description(large_onto)

print()

random.seed(1)

#####
#

# Participant types
high_quality = lambda onto : labeling_generator.Participant(onto, 0.9, 0.9, 0.1)
medium_quality = lambda onto : labeling_generator.Participant(onto, 0.75, 0.75, 0.2)
low_quality = lambda onto : labeling_generator.Participant(onto, 0.6, 0.6, 0.4)

#####
# True labels for each dataset

small_gt = labeling_generator.generate_true_statements(small_onto, 500, 'urn:sample_items:', n_secondary=2)
medium_gt = labeling_generator.generate_true_statements(medium_onto, 500, 'urn:sample_items:', n_secondary=2)
large_gt = labeling_generator.generate_true_statements(large_onto, 500, 'urn:sample_items:', n_secondary=2)

REPS = 10

#####
# Part 1. Redundancy and threshold parameters (OntoVoting)

if True:

    m, s = repeated_label_and_eval(small_gt, medium_quality(small_onto), REPS)
    print(f'One MEDIUM user on a SMALL ontology: {m:.4f} \u00b1 {s:.4f}')

    for redundancy in range(2, 7):
        for threshold in range(1, redundancy+1):
            labelers = [medium_quality(small_onto) for _ in range(redundancy)]
            aggr = aggregation.VotingAggregateLabeler(labelers, threshold)
            m, s = repeated_label_and_eval(small_gt, aggr, REPS)
            print(f'Aggregation with {redundancy} MEDIUM labelers with threshold {threshold} on the SMALL ontology: {m:.4f} \u00b1 {s:.4f}')


#####
# Part 2. Ontology size (OntoVoting)

if True:

    for name, onto, gt in [('Small', small_onto, small_gt), 
                           ('Medium', medium_onto, medium_gt), 
                           ('Large', large_onto, large_gt)]:
        m, s = repeated_label_and_eval(gt, medium_quality(onto), REPS)
        print(f'One MEDIUM user on a {name} ontology: {m:.4f} \u00b1 {s:.4f}')

        for redundancy in [3, 4, 5, 6]:
            labelers = [medium_quality(onto) for _ in range(redundancy)]
            aggr = aggregation.VotingAggregateLabeler(labelers, 2)
            m, s = repeated_label_and_eval(gt, aggr, REPS)
            print(f'Aggregation with {redundancy} MEDIUM labelers on a {name} ontology: {m:.4f} \u00b1 {s:.4f}')

#####
# Part 3. Labelers quality (OntoVoting)
if True:

    for name, foo in [('Low', low_quality), 
                      ('Medium', medium_quality), 
                      ('High', high_quality)]:
        m, s = repeated_label_and_eval(small_gt, foo(small_onto), REPS)
        print(f'One {name} user on a SMALL ontology: {m:.4f} \u00b1 {s:.4f}')

        for redundancy in [3, 4, 5, 6]:
            labelers = [foo(small_onto) for _ in range(redundancy)]
            aggr = aggregation.VotingAggregateLabeler(labelers, 2)
            labels = process_dataset(small_gt, aggr)
            m, s = repeated_label_and_eval(small_gt, aggr, REPS)
            print(f'Aggregation with {redundancy} {name} labelers: {m:.4f} \u00b1 {s:.4f}')

#####
# Part 4. Error distribution
#
if True:

    # Take 1. One medium labeler on a medium ontology
    labels = process_dataset(medium_gt, medium_quality(medium_onto))
    errors = []
    for item in sorted(medium_gt.keys()):
        metric_val = util.metric(medium_gt[item], labels[item])
        if metric_val < 10000:
            errors.append(metric_val)
        else:
            pass # print('Warning: metric undefined (one of the descriptions is empty)')
    np.save('part_4_individual_quality.npy', errors)

    # Take 2. Aggregation
    for redundancy in range(3, 7):
        labelers = [medium_quality(medium_onto) for _ in range(redundancy)]
        aggr = aggregation.VotingAggregateLabeler(labelers, 2)
        labels = process_dataset(medium_gt, aggr)
        errors = []
        for item in sorted(medium_gt.keys()):
            metric_val = util.metric(medium_gt[item], labels[item])
            if metric_val < 10000:
                errors.append(metric_val)
            else:
                pass # print('Warning: metric undefined (one of the descriptions is empty)')
        np.save(f'part_4_aggregated_{redundancy}_quality.npy', errors)
