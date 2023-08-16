import spacy
from rdflib import Graph

# Laden des Spacy-Modells
nlp = spacy.load("en_core_web_sm")

# Laden der OWL-Datei in einen RDF-Graphen
graph = Graph()
graph.parse("AI4PD.owl")

# Funktion zur Durchführung der Abfrage
def perform_query(query):
    results = graph.query(query)
    for result in results:
        print(result)

# Benutzereingabe abfragen
user_input = input("Geben Sie Ihre Anfrage ein: ")

# Verarbeiten der Benutzereingabe mit Spacy
doc = nlp(user_input)

# Erstellen der SPARQL-Abfrage basierend auf der Benutzereingabe
query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    
    SELECT ?result WHERE {
        ?result rdf:type owl:Class .
        ?result rdfs:label ?label .
        FILTER(contains(lcase(str(?label)), lcase("""" + user_input + """")))
    }
"""

# Durchführen der SPARQL-Abfrage
perform_query(query)