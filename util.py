from functools import lru_cache

from owlready2 import *

def print_description(onto):
    print('Base IRI:', onto.base_iri)
    print('Imported ontologies:', list(onto.imported_ontologies))
    print('Number of classes:', len(list(onto.classes())))
    print('Number of individuals:', len(list(onto.individuals())))
    print('Number of object properties:', len(list(onto.object_properties())))
    print('Number of data properties:', len(list(onto.data_properties())))

# Performance analysis has shown that this function is the main
# time consumer (especially, its call to disjoint()). Provided that
# during experiments we do not modify the ontology, generalization
# results can be cached.
# NOTE: Will break if we try to modify the ontology.
# NOTE ALSO: May cause a severe memory sink with large ontologies
@lru_cache(maxsize=None)
def generalization_propagation(onto_cls):
    """
    Lists all the classes that are ancestors of the given class, equivalent to ancestors, and disjoint with them.
    """
    ancestors = list(onto_cls.ancestors())
    negative = []
    for cls in ancestors:
        # Disjoints query for owl:Thing raises an error (which is reasonable)
        if cls == owl.Thing:
            continue
        for d in cls.disjoints():
            negative.extend([x for x in d.entities if x != cls])
    return ancestors, negative

def generalize_statement(prop, val):
    """
    Lists all the generalized versions of some statement (about an implicit object).
    """
    positive_statements = []
    negative_statements = []
    for p in [prop] + prop.is_a:
        if p != owl.ObjectProperty and p != owl.DataProperty:
            pos_class, neg_class = generalization_propagation(val)
            for cls in pos_class:
                positive_statements.append((p, cls))
            for cls in neg_class:
                negative_statements.append((p, cls))
    return positive_statements, negative_statements

# Metric
# Metric is based on two operations:
# - get all the possible generalizations for each statement of A (associated with minimum number of transformations
#   (not counting equivalence)
# - for each statement b of B:
#    - get the list of 'weighted' generalizations
#    - find the smallest sum b to A 
# - do the same in the opposite direction
# - average 
# (Some normalization is also needed!)
def analyse_property(prop):
    q = [(prop, len(prop.is_a))]
    for p in prop.is_a:
        v = len(p.is_a) if p != owl.ObjectProperty else 0
        q.append((p, v))
    q = sorted(q, key = lambda x: x[1])
    mx = max(x[1] for x in q)
    return {k: mx - v for (k, v) in q} 

def analyse_object(obj):
    q = []
    for o in obj.ancestors():
        v = len(o.ancestors()) if o != owl.Thing else 0
        q.append((o, v))
    q = sorted(q, key = lambda x: x[1])
    vs = {}
    v = 0
    for i in reversed(range(len(q))):
        if i < len(q) - 1 and q[i][1] != q[i+1][1]:
            v += 1
        vs[q[i][0]] = v
    return vs 

def statement_generalizations(stmt):
    """Builds all generalizations of the statement and values them."""
    obj = stmt[0]
    prop_generalizations = analyse_property(stmt[1])
    value_generalizations = analyse_object(stmt[2])
    for prop, prop_loss in prop_generalizations.items():
        for val, val_loss in value_generalizations.items():
            yield (obj, prop, val), prop_loss + val_loss

def description_generalizations(descr):
    """Builds a union of generalization for a description (multiple statements)."""
    generalizations = {}
    for stmt in descr:
        for (_, prop, val), stmt_loss in statement_generalizations(stmt):
            current_stmt_loss = generalizations.get((_, prop, val), stmt_loss)  # stmt_loss is default to respect futher min()
            generalizations[(_, prop, val)] = min(stmt_loss, current_stmt_loss)
    return generalizations            

def metric(descr1, descr2):
    """
    Defines how close are two descriptions. 

    Each description is an iterable of some statements (triples). All objects (first component
    of each triple) are considered to be the same (Not tested).
    """

    # The algorithm is the following.
    # 1. Build all possible generalizing statements for each of the descr1 statements.
    # 2. Merge sets, so that 'generalization value' for each of the statements would be minimal.
    # 3. For each of the statements of descr2 find the closest generalization in the merged set.

    total_error = 0
    count = 0
    for _ in range(2):
        generalizations = description_generalizations(descr2)
        for stmt in descr1:
            min_loss = 10000
            for gen_stmt, stmt_loss in statement_generalizations(stmt):
                other_loss = generalizations.get(gen_stmt, 10000)
                if other_loss + stmt_loss < min_loss:
                    min_loss = other_loss + stmt_loss
            if min_loss > 1000:
                pass # print('Warning: the loss is too big')
            total_error += min_loss
            count += 1
        descr1, descr2 = descr2, descr1  # swap
    return total_error # / count

if __name__ == '__main__':

    #onto = get_ontology('ontologies/sample.owl').load()
    onto = get_ontology('ontologies/vldb-crowd.owl').load()

    print_description(onto)

    print('---')
    print(analyse_property(onto.hasPrimaryTopic))
    print('---')
    print(analyse_object(onto.H1C11))
    print('---')
    print(list(statement_generalizations(('XXX', onto.hasPrimaryTopic, onto.H1C11))))
    print('---')
    print(description_generalizations(     [('XXX', onto.hasPrimaryTopic, onto.H1C11),
                                            ('XXX', onto.hasTopic, onto.H1C12),
                                           ]
                                          ))
    print('--- Metric ---')
    print(metric(
                 # Description 1
                 [('XXX', onto.hasPrimaryTopic, onto.H1C11),
                  ('XXX', onto.hasTopic, onto.H1C12),
                 ],
                 [
                 ]))
