# -*- coding: utf-8 -*-

"""This module contains tools for parsing OWL/RDF"""

import urllib
import rdflib
import networkx as nx

from ontospy import Ontospy
from ontospy.ontodocs.viz.viz_html_single import *

__all__ = [
    'parse_owl_rdf',
]


def _find_by_subject(subject, triples):
    triple = None
    for s, p, o in triples:
        if s == subject:
            triple = s, p, o
    return triple


# TODO add another property nodes like Collections, owl:intersectionOf
def get_property_nodes(entity):
    print(entity.bestLabel())

    # copy all triples
    triples = list(entity.triples)
    values = list(filter(lambda x: x[1] == rdflib.term.URIRef('http://www.w3.org/2002/07/owl#hasValue'), triples))
    properties = list(filter(lambda x: x[1] == rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'), triples))

    property_nodes = []

    # create value - property pairs
    # ensure value - property pair correctness by comparing their subjects (either same class or same blank node)
    for val_s, val_p, val_o in values:
        _, _, sub_o = _find_by_subject(val_s, properties)
        print(type(val_o))
        property_nodes.append((entity, sub_o, val_o))

    print(property_nodes)
    return property_nodes


def parse_owl_rdf(iri, generate_prop_nodes=False, visualize=False):
    """Parses an OWL resource that's encoded in OWL/RDF into a NetworkX directional graph

    :param str iri: The location of the OWL resource to be parsed by Ontospy
    :type iri: str
    :rtype: network.DiGraph
    """
    g = nx.DiGraph(IRI=iri)
    o = Ontospy(iri, verbose=True)
    o.build_all()

    print('$' * 20)
    if visualize:
        o.printClassTree()
        v = HTMLVisualizer(o)
        v.build()
        v.preview()
    print(o.all_properties)
    print('$' * 20)

    for cls in o.all_classes:
        g.add_node(cls.bestLabel(), type='Class')

        for parent in cls.parents():
            g.add_edge(cls.bestLabel(), parent.bestLabel(), type='SubClassOf')

        for instance in cls.instances:
            g.add_edge(instance.bestLabel(), cls.bestLabel(), type='ClassAssertion')

        # TODO can reduce complexity by iterating in another loop with o.all_properties
        if generate_prop_nodes:
            for prop in get_property_nodes(cls):
                entity, rel, val_o = prop
                _, value = urllib.parse.urldefrag(str(val_o))
                _, relation = urllib.parse.urldefrag(str(rel))
                g.add_edge(entity.bestLabel(), value, type=relation)

    print(len(g.nodes()))
    return g
