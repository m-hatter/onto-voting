"""
Aggregation methods.
"""

import functools

import util

class VotingRules:
    """
    Summing composition of votes.
    """

    @staticmethod
    def multipath_combine(v1, v2):
        return max(v1, v2)

    @staticmethod
    def negative(v):
        return -v

    @staticmethod
    def combine(v1, v2):
        return v1 + v2

class SBRules:
    """Shortliffe-Buchanan (MYCIN) composition of beliefs.

    Each element of beliefs must be [-1, 1].
    
    See also: https://en.wikipedia.org/wiki/Mycin """

    @staticmethod
    def multipath_combine(v1, v2):
        return max(v1, v2)

    @staticmethod
    def negative(v):
        return -v

    @staticmethod
    def combine(v1, v2):
        if v1 <= 0 and v2 <= 0:
            return v1 + v2 * (1 + v2)
        elif v1 >= 0 and v2 >= 0:
            return v1 + v2 * (1 - v1)
        else:
            return (v1 + v2) / (1 - min(abs(v1), abs(v2)))


def aggregate(descriptions, combination_rules_cls, support_threshold):
    """Descriptions aggregation algorithm."""
    
    # Propagates participant's votes to all the generalizing statements.
    # All the propagated statements are stored in a dict, mapping statement to a list of votes.
    statements = {}
    for belief, description in descriptions:
        this_participant = {}
        for item, prop, val in description:
            pos, neg = util.generalize_statement(prop, val)
            for x in pos:
                stmt = item, x[0], x[1]
                if stmt in this_participant:
                    this_participant[stmt] = combination_rules_cls.multipath_combine(this_participant[stmt], belief)
                else:
                    this_participant[stmt] = belief
            for x in neg:
                stmt = item, x[0], x[1]
                if stmt in this_participant:
                    this_participant[stmt] = combination_rules_cls.multipath_combine(this_participant[stmt], combination_rules_cls.negative(belief))
                else:
                    this_participant[stmt] = combination_rules_cls.negative(belief)
        for stmt, belief in this_participant.items():
            beliefs = statements.setdefault(stmt, [])
            beliefs.append(belief)

    # Increases the value of the statements where there are more than one evidence.
    rstatements = {k: functools.reduce(combination_rules_cls.combine, v) for k, v in statements.items()} 

    # Selects only those statements that are not "covered" by other and have support at least `support_threshold`.
    statements = {k: v for k, v in rstatements.items() if v >= support_threshold}
    statements_list = [s for s in statements]
    for stmt in statements_list:
        # Delete all generalizations of the statement
        if stmt in statements:
            for g_stmt, loss in util.statement_generalizations(stmt):
                if stmt != g_stmt:
                    if g_stmt in statements:
                        del statements[g_stmt]
    return statements

class AggregateLabeler:

    def __init__(self, labelers, combination_cls, support_threshold):
        self.labelers = labelers
        self.combination_cls = combination_cls
        self.support_threshold = support_threshold

    def label_object(self, item, true_description):
        item_descriptions = [(labeler_belief, labeler.label_object(item, true_description)) \
                             for labeler, labeler_belief in self.labelers]
        return [stmt for stmt, belief in aggregate(item_descriptions, 
                                                   self.combination_cls, 
                                                   self.support_threshold).items()]

class VotingAggregateLabeler(AggregateLabeler):

    def __init__(self, labelers, votes_threshold):
        if isinstance(labelers, list):
            super().__init__([(x, 1) for x in labelers], VotingRules, votes_threshold)
        else:
            raise ValueError('Must provide a list of labelers')

class SBAggregateLabeler(AggregateLabeler):

    def __init__(self, labelers, belief_threshold):
        super().__init__(labelers, SBRules, belief_threshold)


if __name__ == '__main__':

    import owlready2

    onto = owlready2.get_ontology('ontologies/vldb-crowd.owl').load()

    util.print_description(onto)

    a = aggregate([(1, [('XXX', onto.hasPrimaryTopic, onto.H1C11),
                      ('XXX', onto.hasTopic, onto.H1C12)]),
               (1, [('XXX', onto.hasPrimaryTopic, onto.H1C11),
               #       ('XXX', onto.hasTopic, onto.H1C12)
                     ]),
              ], VotingRules, 2)
    print(a)

    #print(metric(onto,
    #             # Description 1
    #             [('XXX', onto.hasPrimaryTopic, onto.H1C11),
    #              ('XXX', onto.hasTopic, onto.H1C12),
    #             ],
    #             [
    #             ]))

