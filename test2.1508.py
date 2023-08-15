import tkinter as tk
import tkinter.ttk as ttk
import spacy
from tkinter.messagebox import showinfo
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
from tkinter.filedialog import askopenfilename
import os

def extract_ai4pd_part(item):
    parts = item.split('AI4PD:')
    if len(parts) == 2:
        return 'AI4PD:' + parts[1]
    else:
        return None

def get_unique_subjects(graph):
    query = prepareQuery("SELECT DISTINCT ?s WHERE {?s ?p ?o}")
    results = graph.query(query)
    unique_subjects = [str(result[0]) for result in results]
    return [extract_ai4pd_part(item) for item in unique_subjects if 'AI4PD:' in item]

def get_unique_predicates(graph):
    query = prepareQuery("SELECT DISTINCT ?p WHERE {?s ?p ?o}")
    results = graph.query(query)
    unique_predicates = [str(result[0]) for result in results]
    return [extract_ai4pd_part(item) for item in unique_predicates if 'AI4PD:' in item]

def get_unique_objects(graph):
    query = prepareQuery("SELECT DISTINCT ?o WHERE {?s ?p ?o}")
    results = graph.query(query)
    unique_objects = [str(result[0]) for result in results]
    return [extract_ai4pd_part(item) for item in unique_objects if 'AI4PD:' in item]

def get_all_individuals(owl_file, query):
    owl = Namespace("http://www.w3.org/2002/07/owl#")
    graph = Graph()
    graph.parse(owl_file)
    prepared_query = prepareQuery(query)
    results = graph.query(prepared_query)
    return results

def execute_query(event=None):
    query = query_text.get("1.0", tk.END).strip()
    results = get_all_individuals(owl_file_path, query)
    result_text.delete("1.0", tk.END)
    for row in results:
        result = [str(term).split('/')[-1] for term in row]
        result_text.insert(tk.END, ' '.join(result) + "\n")

def process_text():
    text = input_text.get("1.0", tk.END).strip()
    if text:
        doc = nlp(text)
        output_text.delete("1.0", tk.END)

        tokens = [token.text for token in doc]
        tokenized_text = ' '.join(tokens)
        output_text.insert(tk.END, "Tokenisiert: " + tokenized_text + "\n\n")

        pos_tags = [(token.text, token.pos_) for token in doc]
        pos_tags_text = '\n'.join([f"{token}: {pos}" for token, pos in pos_tags])
        output_text.insert(tk.END, "Wortarten:\n" + pos_tags_text + "\n\n")

        entities = [(ent.text, ent.label_) for ent in doc.ents]
        entities_text = '\n'.join([f"{entity}: {label}" for entity, label in entities])
        output_text.insert(tk.END, "Benannte Entitäten:\n" + entities_text + "\n\n")

        lemmas = [token.lemma_ for token in doc]
        lemmatized_text = ' '.join(lemmas)
        output_text.insert(tk.END, "Lemmas: " + lemmatized_text + "\n\n")

        dependencies = [(token.text, token.dep_, token.head.text) for token in doc]
        dependencies_text = '\n'.join([f"{token}: {dep} --> {head}" for token, dep, head in dependencies])
        output_text.insert(tk.END, "Abhängigkeitssyntax:\n" + dependencies_text)

def select_owl_file():
    global owl_file_path
    owl_file_path = askopenfilename(filetypes=[("OWL Files", "*.owl")])
    if owl_file_path:
        file_name = os.path.basename(owl_file_path)
        selected_file_label.config(text="Selected File: " + file_name)
        graph = Graph()
        graph.parse(owl_file_path)
        unique_subjects = get_unique_subjects(graph)
        unique_predicates = get_unique_predicates(graph)
        unique_objects = get_unique_objects(graph)
        dropdown_subject['values'] = unique_subjects
        dropdown_predicate['values'] = unique_predicates
        dropdown_object['values'] = unique_objects
    else:
        owl_file_path = ""
        selected_file_label.config(text="No File Selected")

def create_query():
    selected_values = [dropdown.get() for dropdown in dropdowns]
    query_part = ''
    if all(value == 'none' for value in selected_values):
        showinfo('Error', 'Please select at least one value.')
        return
    else:
        for i, value in enumerate(selected_values):
            if value != 'none':
                query_part += f'{value} '
            if (i + 1) % 3 == 0 or i == len(selected_values) - 1:
                if i != len(selected_values) - 1:
                    query_part += '.\n'

    current_query = query_text.get("1.0", tk.END).strip()
    if "}" in current_query:
        current_query = current_query.replace("}", f"{query_part}\n}}")
    else:
        current_query += f"\n\nPREFIX AI4PD: <http://www.semanticweb.org/gerschuetz/forcude/AI4PD:>\nselect * where {{\n{query_part}\n}}"
    query_text.delete('1.0', tk.END)
    query_text.insert(tk.END, current_query)
    
    # Reset the dropdowns
    for dropdown in dropdowns:
        dropdown.set('')

nlp = spacy.load("de_core_news_sm")
window = tk.Tk()
window.title("SPARQL Query & NLP GUI")

style = ttk.Style()
style.configure('TButton', font=('Arial', 12))
style.configure('TLabel', font=('Arial', 12))
style.configure('TEntry', font=('Arial', 12))
style.configure('TText', font=('Arial', 12))

query_label = ttk.Label(window, text="SPARQL Query:")
query_label.pack()
query_text = tk.Text(window, height=10, width=50, wrap="word")
query_text.pack()
query_text.insert(tk.END, "PREFIX AI4PD: <http://www.semanticweb.org/gerschuetz/forcude/AI4PD:>\n   SELECT *\n    WHERE {\n        ?individual a owl:NamedIndividual .\n    }")

select_file_button = ttk.Button(window, text="Select OWL File", command=select_owl_file)
select_file_button.pack()

selected_file_label = ttk.Label(window, text="No File Selected")
selected_file_label.pack()

subject_label = ttk.Label(window, text="Subject:")
subject_label.pack()
dropdown_subject = ttk.Combobox(window)
dropdown_subject.pack()

predicate_label = ttk.Label(window, text="Predicate:")
predicate_label.pack()
dropdown_predicate = ttk.Combobox(window)
dropdown_predicate.pack()

object_label = ttk.Label(window, text="Object:")
object_label.pack()
dropdown_object = ttk.Combobox(window)
dropdown_object.pack()

dropdowns = [dropdown_subject, dropdown_predicate, dropdown_object]

# Create a frame to hold the buttons side by side
button_frame = ttk.Frame(window)
button_frame.pack(pady=10)

add_to_query_button = ttk.Button(button_frame, text="Add to Query", command=create_query)
add_to_query_button.pack(side=tk.LEFT, padx=10)

query_button = ttk.Button(button_frame, text="Execute", command=execute_query)
query_button.pack(side=tk.LEFT)

result_label = ttk.Label(window, text="Query Result:")
result_label.pack()
result_text = tk.Text(window, height=5, width=50, wrap="word")
result_text.pack()

input_label = ttk.Label(window, text="Input Text:")
input_label.pack()
input_text = tk.Text(window, height=5, width=50, wrap="word")
input_text.pack()
input_text.insert(tk.END, "Hallo, ich bin ein Text. Ich stehe hier um die Funktion von NLP zu testen.")

process_button = ttk.Button(window, text="Process Text", command=process_text)
process_button.pack()
output_label = ttk.Label(window, text="Output:")
output_label.pack()
output_text = tk.Text(window, height=5, width=50, wrap="word")
output_text.pack()

window.bind('<Return>', execute_query)
window.mainloop()
