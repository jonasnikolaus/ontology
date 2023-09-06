import spacy
from rdflib import Graph, URIRef

# Lade das SpaCy-Modell
nlp = spacy.load("de_core_news_sm")

# Lade die OWL-Datei in einen RDF-Graph
graph = Graph()
graph.parse("AI4PD.owl")

def perform_query(query, keywords):
    # Führe die SPARQL-Abfrage auf dem Graph aus
    results = graph.query(query)
    
    # Filtere die Ergebnisse basierend auf den Schlüsselwörtern
    filtered_results = [str(row.tool) for row in results if any(keyword in str(row.tool).lower() for keyword in keywords)]
    
    # Gib die gefilterten Ergebnisse aus
    for item in filtered_results:
        print(item)
    print("--------------------")

# Nutzereingabe abfragen
user_input = input("Geben Sie Ihre Anfrage ein: ")

# Verarbeite die Nutzereingabe mit SpaCy
doc = nlp(user_input)

# Extrahiere Schlüsselwörter aus der Nutzereingabe
keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]]

# Erstelle eine SPARQL-Abfrage basierend auf den Schlüsselwörtern
query_template = """
SELECT ?subject ?object
	WHERE {{ ?subject rdfs:subClassOf ?object }}
"""

# Führe die SPARQL-Abfrage aus
perform_query(query_template, keywords)
