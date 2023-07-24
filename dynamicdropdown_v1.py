import os
import tkinter as tk
import tkinter.ttk as ttk
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from tkinter.filedialog import askopenfilename


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


# Create main window
window = tk.Tk()
window.title("SPARQL Query GUI")

# Create label and dropdown for subjects
subject_label = ttk.Label(window, text="Subject:")
subject_label.pack()
dropdown_subject = ttk.Combobox(window)
dropdown_subject.pack()

# Create label and dropdown for predicates
predicate_label = ttk.Label(window, text="Predicate:")
predicate_label.pack()
dropdown_predicate = ttk.Combobox(window)
dropdown_predicate.pack()

# Create label and dropdown for objects
object_label = ttk.Label(window, text="Object:")
object_label.pack()
dropdown_object = ttk.Combobox(window)
dropdown_object.pack()

# Create button to select OWL file
select_file_button = ttk.Button(window, text="Select OWL File", command=select_owl_file)
select_file_button.pack()

# Create label to display selected file
selected_file_label = ttk.Label(window, text="No File Selected")
selected_file_label.pack()

# Start GUI loop
window.mainloop()
