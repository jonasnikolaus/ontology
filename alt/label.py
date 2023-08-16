from owlready2 import *

# Laden der OWL-Datei
onto = get_ontology("AI4PD.owl").load()

# Iteration über die Entitäten und Ausgabe der Labels
for entity in onto.classes():
    if entity.label:
        print(entity.label[0])