from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

# Lade die OWL-Datei in eine Graph-Instanz
g = Graph()
g.parse("AI4PD.owl")

# Definiere die SPARQL-Abfrage
q = prepareQuery('''
SELECT ?DataDrivenTask ?DataDrivenMethod ?DataDrivenTool
WHERE {
    ?DataDrivenTask , ?DataDrivenMethod , ?DataDrivenTool .
    ?AI4PD :Team AI4PD:hasValue SimulationDepartment ;
           AI4PD:SubProcess AI4PD:hasValue Simulation ;
           AI4PD:DataIn ?in ;
           AI4PD:hasStorage AI4PD:PDM-System .
    ?in AI4PD:hasFormat ?formatIn .
    ?AI4PD:DataOut ;
          AI4PD:hasFormat ?formatOut ;
          AI4PD:hasStorage AI4PD:SDM-System .
    ?AI4PD:TrainingHardware AI4PD:hasValue GPUBased .
    ?AI4PD:UsageHardware ;
          AI4PD:hasComputingPower AI4PD:lowComputing ;
          AI4PD:hasInterface AI4PD:commandLine .
    FILTER (?formatIn IN (AI4PD:CADData, AI4PD:CSVData))
    FILTER (?formatOut IN (AI4PD:FEMResult, AI4PD:CSVData))
}
''')

# Führe die Abfrage aus und gib die Ergebnisse aus
results = g.query(q, initNs={'AI4PD': "http://www.semanticweb.org/jonasnikolaus/ontologies/2022/3/AI4PD#"})
for row in results:
    print(row)
