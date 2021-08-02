"""
Algorithms for generating ground truth and user model.
"""
import random

from owlready2 import *

import util

class Participant:
    """
    Participant profile.

    Used to generate statements with certain error probability.
    """

    def __init__(self, ontology, observancy, diligence, noise):
        self.onto = ontology
        self.observancy = observancy
        self.diligence = diligence
        self.noise = noise

    def label_object(self, item, true_description):
        """
        Label the specified item. Returns a list of statements.
        """
        description = []
        for item, prop, val in true_description:
            if random.random() < self.observancy:
                # Generalize property:
                # Just selects one of the ancestors
                if random.random() < 1 - self.diligence:
                    ancestors = [x for x in prop.is_a if x != owl.ObjectProperty and x != owl.DataProperty]
                    prop = random.choice(ancestors) if len(ancestors) > 1 else prop
                # Generalize value:
                # Again, just selects one of the ancestors
                if random.random() < 1 - self.diligence:
                    ancestors = [x for x in val.ancestors() if x != owl.Thing and x != val]
                    val = random.choice(ancestors) if len(ancestors) > 1 else val
                description.append((item, prop, val))
            else:
                # overlooked
                pass
        # Add some noise
        while True:
            if random.random() < self.noise:
                prop = random.choice([x for x in self.onto.object_properties() if x != owl.ObjectProperty])
                val = random.choice([x for x in self.onto.classes() if x != owl.Thing])
                description.append((item, prop, val))
            else:
                break
        # If no statements were generated, then select one from true randomly:
        if not description:
            description = [random.choice(true_description)]
        return description

def generate_true_statements(onto, n_items, prefix, n_secondary=2):
    """
    Generates true description for the specified number of items.

    Note, that this function is ontology-specific. E.g., it 
    relies on the fact that there are several hierarchies in the ontology
    and uses values of different hierarchies for different statements.
    """
    item_descriptions = {}
    available_classes = [x for x in onto.classes() if x != owl.Thing and x != onto.Item]
    for i in range(n_items):
        item = prefix + 'item' + str(i)
        item_description = []
        # select a primary topic
        primary_topic = random.choice(available_classes)
        item_description.append((item, onto.hasPrimaryTopic, primary_topic))
        for _ in range(n_secondary):
            secondary_topic = random.choice(available_classes)
            if secondary_topic not in primary_topic.ancestors() and \
               secondary_topic not in primary_topic.descendants():
                item_description.append((item, onto.hasTopic, secondary_topic))
        item_descriptions[item] = item_description
    return item_descriptions

if __name__ == '__main__':

    # TODO: Looks like labeling is not reprobucible because of Python hash variations: ancestors, descendants order.

    onto = get_ontology('ontologies/vldb-crowd.owl').load()
    print()

    random.seed(3)

    ground_truth = generate_true_statements(onto, 20, 'urn:sample_items:')

    participant = Participant(onto, 0.8, 0.8, 0.3)
    s = 0
    for item in sorted(ground_truth.keys()):
        labels = participant.label_object(item, ground_truth[item])
        s += util.metric(onto, ground_truth[item], labels)
    print('Loss:', s / len(ground_truth))

