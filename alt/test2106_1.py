import tkinter as tk
import tkinter.ttk as ttk
import spacy
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
from tkinter.filedialog import askopenfilename
import os

def get_all_individuals(owl_file, query):
    # OWL Namespace
    owl = Namespace("http://www.w3.org/2002/07/owl#")

    # Load the OWL file
    graph = Graph()
    graph.parse(owl_file)

    # Prepare the SPARQL query
    prepared_query = prepareQuery(query)

    # Execute the query
    results = graph.query(prepared_query)

    # Return the results
    return results

def execute_query(event=None):
    # Get the user query from the input field
    query = query_text.get("1.0", tk.END).strip()

    # Execute the query on the OWL file
    results = get_all_individuals(owl_file_path, query)

    # Clear the result text widget
    result_text.delete("1.0", tk.END)

    # Display the results in the result text widget
    for row in results:
        result_text.insert(tk.END, str(row) + "\n")

    # Set focus on the query text widget
    query_text.focus()

def process_text():
    text = input_text.get("1.0", tk.END).strip()
    if text:
        doc = nlp(text)
        
        # Clear the output text widget
        output_text.delete("1.0", tk.END)
        
        # Tokenisierung
        tokens = [token.text for token in doc]
        tokenized_text = ' '.join(tokens)
        output_text.insert(tk.END, "Tokenisiert: " + tokenized_text + "\n\n")
        
        # Part-of-Speech-Tagging
        pos_tags = [(token.text, token.pos_) for token in doc]
        pos_tags_text = '\n'.join([f"{token}: {pos}" for token, pos in pos_tags])
        output_text.insert(tk.END, "Wortarten:\n" + pos_tags_text + "\n\n")
        
        # Named Entity Recognition (NER)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        entities_text = '\n'.join([f"{entity}: {label}" for entity, label in entities])
        output_text.insert(tk.END, "Benannte Entitäten:\n" + entities_text + "\n\n")
        
        # Lemmatisierung
        lemmas = [token.lemma_ for token in doc]
        lemmatized_text = ' '.join(lemmas)
        output_text.insert(tk.END, "Lemmas: " + lemmatized_text + "\n\n")
        
        # Abhängigkeitssyntax
        dependencies = [(token.text, token.dep_, token.head.text) for token in doc]
        dependencies_text = '\n'.join([f"{token}: {dep} --> {head}" for token, dep, head in dependencies])
        output_text.insert(tk.END, "Abhängigkeitssyntax:\n" + dependencies_text)

    # Set focus on the input text widget
    input_text.focus()

def select_owl_file():
    global owl_file_path
    owl_file_path = askopenfilename(filetypes=[("OWL Files", "*.owl")])
    if owl_file_path:
        file_name = os.path.basename(owl_file_path)
        selected_file_label.config(text="Selected File: " + file_name)
    else:
        owl_file_path = ""
        selected_file_label.config(text="No File Selected")

# Initialisiere Spacy mit dem gewünschten Sprachmodell
nlp = spacy.load("de_core_news_sm")

# Erstelle das Hauptfenster
window = tk.Tk()
window.title("SPARQL Query & NLP GUI")

# Style
style = ttk.Style()
style.configure('TButton', font=('Arial', 12))
style.configure('TLabel', font=('Arial', 12))
style.configure('TEntry', font=('Arial', 12))
style.configure('TText', font=('Arial', 12))

# SPARQL Query Section
query_label = ttk.Label(window, text="SPARQL Query:")
query_label.pack()
query_text = tk.Text(window, height=10, width=50, wrap="word")
query_text.pack()
query_text.insert(tk.END, "SELECT ?individual\n    WHERE {\n        ?individual a owl:NamedIndividual .\n    }")

# OWL File Section
select_file_button = ttk.Button(window, text="Select OWL File", command=select_owl_file)
select_file_button.pack()

selected_file_label = ttk.Label(window, text="No File Selected")
selected_file_label.pack()

query_button = ttk.Button(window, text="Execute", command=execute_query)
query_button.pack()

result_label = ttk.Label(window, text="Query Result:")
result_label.pack()
result_text = tk.Text(window, height=10, width=50, wrap="word")
result_text.pack()

# NLP Section
input_label = ttk.Label(window, text="Input Text:")
input_label.pack()
input_text = tk.Text(window, height=10, width=50, wrap="word")
input_text.pack()
input_text.insert(tk.END, "Hallo, ich bin ein Text. Ich stehe hier um die Funktion von NLP zu testen.")

process_button = ttk.Button(window, text="Process Text", command=process_text)
process_button.pack()
output_label = ttk.Label(window, text="Output:")
output_label.pack()
output_text = tk.Text(window, height=20, width=50, wrap="word")
output_text.pack()

# Set focus on the input text at startup
input_text.focus()

# Bind Return key to execute_query
window.bind('<Return>', execute_query)

# Starte die GUI-Schleife
window.mainloop()

# alle tools in toolbox rapidminer
# tool und toolbox die den regressiontree m5p implementieren
# sparql bibliothek für python, so dass keine syntax nötig 