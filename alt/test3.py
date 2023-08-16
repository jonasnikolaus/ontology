from rdflib import Graph, Namespace, Literal
from rdflib.plugins.sparql import prepareQuery

def get_entity_by_name(owl_file, entity_name):
    # OWL Namespace
    owl = Namespace("http://www.w3.org/2002/07/owl#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

    # Load the OWL file
    graph = Graph()
    graph.parse(owl_file)

    # Prepare the SPARQL query
    query_template = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?entity
    WHERE {{
        ?entity a owl:Class ;
                rdfs:label ?label .
        FILTER(STR(?label) = "{}")
    }}
    """
    query = prepareQuery(query_template.format(entity_name))

    # Execute the query
    results = graph.query(query)

    # Print the results
    for row in results:
        print(row.entity)

# Test the program
owl_file = "AI4PD.owl"
entity_name = "AI4PD:CSVData"
get_entity_by_name(owl_file, entity_name)
