import types
import random

from owlready2 import *

import util

def generate_hierarchy(onto, prefix, levels, branching, disjoint=False):
    """
    Generates a hierarchy of classes connected by owl:SubClassOf property.
    """
    def gen_h(root, p, l):
        if l < 1:
            return
        with onto:
            this_level = []
            for i in range(1, branching + 1):
                class_name = p + str(i)
                cls = types.new_class(class_name, (root, ))
                this_level.append(cls)
                gen_h(cls, class_name, l - 1)
            if disjoint:
                AllDisjoint(this_level)

    gen_h(owl.Thing, prefix, levels)

SYNONIMS_RATIO = 0.3
SYNONIM_PREFIX = 'S'

def create_small_ontology():

    onto = get_ontology('http://cais.iias.spb.su/ontology/generated/ontoagg_small/')
    
    print(onto.base_iri)

    # The sample ontology used in the experiments contains several
    # classification hierarchies (of varying depth and branching)
    generate_hierarchy(onto, 'H1C', 4, 3, disjoint=True)
    generate_hierarchy(onto, 'H2C', 4, 3, disjoint=False)

    # Some number of equivalent classes
    real_classes = list(onto.classes())
    synonims_count = int(len(real_classes) * SYNONIMS_RATIO)
    with onto:
        for i in range(synonims_count):
            cls = types.new_class(SYNONIM_PREFIX + str(i), (owl.Thing, ))
            cls.equivalent_to.append(random.choice(real_classes))

    # Item class
    with onto:
        class Item(owl.Thing):
            pass

    # And a small hierarchy of properties, connecting items to classes
    with onto:
        class hasTopic(ObjectProperty):
            domain    = [onto.Item]
            #range     = []
        class hasPrimaryTopic(hasTopic):
            pass
        class hasP1(ObjectProperty):
            domain    = [onto.Item]
        class hasP11(hasP1):
            pass
        class hasP12(hasP1):
            pass
    
    util.print_description(onto)        

    onto.save('ontologies\\ontoagg_small.owl')

def create_medium_ontology():

    onto = get_ontology('http://cais.iias.spb.su/ontology/generated/ontoagg_medium/')
    
    print(onto.base_iri)

    # The sample ontology used in the experiments contains several
    # classification hierarchies (of varying depth and branching)
    generate_hierarchy(onto, 'H1C', 4, 3, disjoint=True)
    generate_hierarchy(onto, 'H2C', 4, 3, disjoint=False)
    generate_hierarchy(onto, 'H3C', 4, 4, disjoint=True)
    generate_hierarchy(onto, 'H4C', 4, 4, disjoint=False)

    # Some number of equivalent classes
    real_classes = list(onto.classes())
    synonims_count = int(len(real_classes) * SYNONIMS_RATIO)
    with onto:
        for i in range(synonims_count):
            cls = types.new_class(SYNONIM_PREFIX + str(i), (owl.Thing, ))
            cls.equivalent_to.append(random.choice(real_classes))

    # Item class
    with onto:
        class Item(owl.Thing):
            pass

    # And a small hierarchy of properties, connecting items to classes
    with onto:
        class hasTopic(ObjectProperty):
            domain    = [onto.Item]
            #range     = []
        class hasPrimaryTopic(hasTopic):
            pass
        class hasP1(ObjectProperty):
            domain    = [onto.Item]
        class hasP11(hasP1):
            pass
        class hasP12(hasP1):
            pass
    
    util.print_description(onto)        

    onto.save('ontologies\\ontoagg_medium.owl')

def create_large_ontology():

    onto = get_ontology('http://cais.iias.spb.su/ontology/generated/ontoagg_large/')
    
    print(onto.base_iri)

    # The sample ontology used in the experiments contains several
    # classification hierarchies (of varying depth and branching)
    generate_hierarchy(onto, 'H1C', 4, 3, disjoint=True)
    generate_hierarchy(onto, 'H2C', 4, 3, disjoint=False)
    generate_hierarchy(onto, 'H3C', 4, 4, disjoint=True)
    generate_hierarchy(onto, 'H4C', 4, 4, disjoint=False)
    generate_hierarchy(onto, 'H5C', 4, 3, disjoint=True)
    generate_hierarchy(onto, 'H6C', 4, 3, disjoint=False)
    generate_hierarchy(onto, 'H7C', 4, 4, disjoint=True)
    generate_hierarchy(onto, 'H8C', 4, 4, disjoint=False)

    # Some number of equivalent classes
    real_classes = list(onto.classes())
    synonims_count = int(len(real_classes) * SYNONIMS_RATIO)
    with onto:
        for i in range(synonims_count):
            cls = types.new_class(SYNONIM_PREFIX + str(i), (owl.Thing, ))
            cls.equivalent_to.append(random.choice(real_classes))

    # Item class
    with onto:
        class Item(owl.Thing):
            pass

    # And a small hierarchy of properties, connecting items to classes
    with onto:
        class hasTopic(ObjectProperty):
            domain    = [onto.Item]
            #range     = []
        class hasPrimaryTopic(hasTopic):
            pass
        class hasP1(ObjectProperty):
            domain    = [onto.Item]
        class hasP11(hasP1):
            pass
        class hasP12(hasP1):
            pass
    
    util.print_description(onto)        

    onto.save('ontologies\\ontoagg_large.owl')


if __name__ == '__main__':

    random.seed(1)
    create_small_ontology()

    random.seed(1)
    create_medium_ontology()

    random.seed(1)
    create_large_ontology()
