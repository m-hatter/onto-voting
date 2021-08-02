import owlready2

import util
import aggregation

def test_generalization():
    # Set-up
    small_onto = owlready2.get_ontology('ontologies/ontoagg_small.owl').load()
    medium_onto = owlready2.get_ontology('ontologies/ontoagg_medium.owl').load()

    pos, neg = util.generalization_propagation(small_onto.H1C12)
    assert(frozenset(pos) == frozenset([small_onto.H1C12, 
                                        small_onto.H1C1, small_onto.S26,
                                        owlready2.owl.Thing]))
    assert(frozenset(neg) == frozenset([small_onto.H1C13, small_onto.H1C11, 
                                        small_onto.H1C2, small_onto.H1C3]))  # disjoint hierarchy

    pos, neg = util.generalization_propagation(small_onto.H2C22)
    assert(frozenset(pos) == frozenset([small_onto.H2C22, 
                                        small_onto.H2C2,
                                        owlready2.owl.Thing]))
    assert(not neg) # this hierarchy is not disjoint

    # Check that two ontologies do not interfere
    pos, neg = util.generalization_propagation(medium_onto.H1C12)
    assert(frozenset(pos) == frozenset([medium_onto.H1C12, medium_onto.S222, 
                                        medium_onto.H1C1,
                                        owlready2.owl.Thing]))
    assert(frozenset(neg) == frozenset([medium_onto.H1C13, medium_onto.H1C11, 
                                        medium_onto.H1C2, medium_onto.H1C3]))  # disjoint hierarchy


def test_aggregation():
    # Set-up
    small_onto = owlready2.get_ontology('ontologies/ontoagg_small.owl').load()

    a = aggregation.aggregate([(1, [('XXX', small_onto.hasPrimaryTopic, small_onto.H1C11),
                                    ('XXX', small_onto.hasTopic, small_onto.H1C12)]),
                               (1, [('XXX', small_onto.hasPrimaryTopic, small_onto.H1C11),
                                   ]),
                              ], aggregation.VotingRules, 2)
    assert(frozenset(a.keys()) == frozenset([('XXX', small_onto.hasPrimaryTopic, small_onto.H1C11)]))

    a = aggregation.aggregate([(1, [('XXX', small_onto.hasPrimaryTopic, small_onto.H1C11),
                                    ('XXX', small_onto.hasTopic, small_onto.H2C12)]),
                               (1, [('XXX', small_onto.hasPrimaryTopic, small_onto.H1C12),
                                   ]),
                              ], aggregation.VotingRules, 2)
    assert(frozenset(a.keys()) == frozenset([('XXX', small_onto.hasPrimaryTopic, small_onto.H1C1)]) or \
           frozenset(a.keys()) == frozenset([('XXX', small_onto.hasPrimaryTopic, small_onto.S26)]))

    a = aggregation.aggregate([(0.8, [('XXX', small_onto.hasPrimaryTopic, small_onto.H1C11),
                                    ('XXX', small_onto.hasTopic, small_onto.H2C12)]),
                               (0.7, [('XXX', small_onto.hasPrimaryTopic, small_onto.H1C12),
                                   ]),
                              ], aggregation.SBRules, 0.92)
    assert(frozenset(a.keys()) == frozenset([('XXX', small_onto.hasPrimaryTopic, small_onto.H1C1)]) or \
           frozenset(a.keys()) == frozenset([('XXX', small_onto.hasPrimaryTopic, small_onto.S26)]))


if __name__ == '__main__':

    test_generalization()
    test_aggregation()