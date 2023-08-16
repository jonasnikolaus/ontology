from rdflib import Graph, Namespace

def generate_sparql_queries(owl_file):
    # OWL Namespace
    owl = Namespace("http://www.w3.org/2002/07/owl#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

    # Load the OWL file
    graph = Graph()
    graph.parse(owl_file)

    # Generate SPARQL queries
    queries = []

    # Query 1: List all classes
    query_classes = """
    SELECT DISTINCT ?class
    WHERE {
        ?class a owl:Class.
    }
    """
    queries.append(query_classes)

    # Query 2: List all object properties
    query_object_properties = """
    SELECT DISTINCT ?property
    WHERE {
        ?property a owl:ObjectProperty.
    }
    """
    queries.append(query_object_properties)

    # Query 3: List all data properties
    query_data_properties = """
    SELECT DISTINCT ?property
    WHERE {
        ?property a owl:DatatypeProperty.
    }
    """
    queries.append(query_data_properties)

    # Query 4: List all individuals
    query_individuals = """
    SELECT DISTINCT ?individual
    WHERE {
        ?individual a owl:NamedIndividual.
    }
    """
    queries.append(query_individuals)

    # Query 5: List all subclasses
    query_subclasses = """
    SELECT DISTINCT ?subclass
    WHERE {
        ?subclass rdfs:subClassOf ?superclass.
    }
    """
    queries.append(query_subclasses)

    # Query 6: List all object properties and their domains and ranges
    query_properties_domains_ranges = """
    SELECT DISTINCT ?property ?domain ?range
    WHERE {
        ?property a owl:ObjectProperty.
        OPTIONAL { ?property rdfs:domain ?domain. }
        OPTIONAL { ?property rdfs:range ?range. }
    }
    """
    queries.append(query_properties_domains_ranges)

    # Query 7: List all data properties and their domains and ranges
    query_data_properties_domains_ranges = """
    SELECT DISTINCT ?property ?domain ?range
    WHERE {
        ?property a owl:DatatypeProperty.
        OPTIONAL { ?property rdfs:domain ?domain. }
        OPTIONAL { ?property rdfs:range ?range. }
    }
    """
    queries.append(query_data_properties_domains_ranges)

    # Execute and print the queries
    for query in queries:
        results = graph.query(query)
        print("Query:", query)
        print("Results:")
        for row in results:
            print(row)
        print()

# Test the program
owl_file = "AI4PD.owl"
generate_sparql_queries(owl_file)
