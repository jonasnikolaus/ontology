from rdflib import Graph

def load_and_query_owl(file_path, query):
    # RDF-Graph erstellen
    graph = Graph()

    # OWL-Datei laden
    try:
        graph.parse(file_path, format="xml")
        print("Graph erfolgreich geladen. Anzahl Tripel:", len(graph))
    except Exception as e:
        print("Fehler beim Laden der OWL-Datei:", e)
        return

    # SPARQL-Abfrage ausführen
    try:
        results = graph.query(query)
        for result in results:
            print(result)
        if not results:
            print("Keine Ergebnisse gefunden.")
    except Exception as e:
        print("Fehler bei der SPARQL-Abfrage:", e)

# Pfad zu Ihrer OWL-Datei
owl_file_path = "/Users/jonasnikolaus/Downloads/Ontologie/AI4PD.owl"

# Ihre SPARQL-Abfrage
sparql_query = """
PREFIX AI4PD: <http://www.semanticweb.org/gerschuetz/forcude/AI4PD:>
SELECT * WHERE {
    ?instance a AI4PD:Tool .
}
"""

# Funktion aufrufen
load_and_query_owl(owl_file_path, sparql_query)
