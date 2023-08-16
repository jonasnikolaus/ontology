import spacy
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
import PySimpleGUI as sg
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

def execute_query():
    query = values['query_text'].strip()
    results = get_all_individuals(owl_file_path, query)
    result_texts = []
    for row in results:
        result = [str(term).split('/')[-1] for term in row]
        result_texts.append(' '.join(result))
    window['result_text'].update('\n'.join(result_texts))

def process_text():
    text = values['input_text'].strip()
    if text:
        doc = nlp(text)
        output_texts = []

        tokens = [token.text for token in doc]
        tokenized_text = ' '.join(tokens)
        output_texts.append("Tokenisiert: " + tokenized_text)

        pos_tags = [(token.text, token.pos_) for token in doc]
        pos_tags_text = '\n'.join([f"{token}: {pos}" for token, pos in pos_tags])
        output_texts.append("Wortarten:\n" + pos_tags_text)

        entities = [(ent.text, ent.label_) for ent in doc.ents]
        entities_text = '\n'.join([f"{entity}: {label}" for entity, label in entities])
        output_texts.append("Benannte Entitäten:\n" + entities_text)

        lemmas = [token.lemma_ for token in doc]
        lemmatized_text = ' '.join(lemmas)
        output_texts.append("Lemmas: " + lemmatized_text)

        dependencies = [(token.text, token.dep_, token.head.text) for token in doc]
        dependencies_text = '\n'.join([f"{token}: {dep} --> {head}" for token, dep, head in dependencies])
        output_texts.append("Abhängigkeitssyntax:\n" + dependencies_text)

        window['output_text'].update('\n\n'.join(output_texts))

def select_owl_file():
    global owl_file_path
    owl_file_path = sg.popup_get_file('Select OWL File', file_types=(("OWL Files", "*.owl"),))
    if owl_file_path:
        file_name = os.path.basename(owl_file_path)
        window['selected_file_label'].update("Selected File: " + file_name)
        graph = Graph()
        graph.parse(owl_file_path)
        unique_subjects = get_unique_subjects(graph)
        unique_predicates = get_unique_predicates(graph)
        unique_objects = get_unique_objects(graph)
        window['dropdown_subject'].update(values=unique_subjects)
        window['dropdown_predicate'].update(values=unique_predicates)
        window['dropdown_object'].update(values=unique_objects)
    else:
        owl_file_path = ""
        window['selected_file_label'].update("No File Selected")

def create_query():
    selected_values = [values['dropdown_subject'], values['dropdown_predicate'], values['dropdown_object']]
    query_part = ''
    if all(value == '' for value in selected_values):
        sg.popup_error('Error', 'Please select at least one value.')
        return
    else:
        for i, value in enumerate(selected_values):
            if value:
                query_part += f'{value} '
            if (i + 1) % 3 == 0 or i == len(selected_values) - 1:
                if i != len(selected_values) - 1:
                    query_part += '.\n'

    current_query = values['query_text'].strip()
    if "}" in current_query:
        current_query = current_query.replace("}", f"{query_part}\n}}")
    else:
        current_query += f"\n\nPREFIX AI4PD: <http://www.semanticweb.org/gerschuetz/forcude/AI4PD:>\nselect * where {{\n{query_part}\n}}"
    window['query_text'].update(current_query)

nlp = spacy.load("de_core_news_sm")

layout = [
    [sg.Text("SPARQL Query:")],
    [sg.Multiline("", size=(50, 10), key="query_text")],
    [sg.Button("Select OWL File", key="select_file_button")],
    [sg.Text("No File Selected", size=(40, 1), key="selected_file_label")],
    [sg.Text("Subject:"), sg.Combo([], size=(40, 1), key="dropdown_subject")],
    [sg.Text("Predicate:"), sg.Combo([], size=(40, 1), key="dropdown_predicate")],
    [sg.Text("Object:"), sg.Combo([], size=(40, 1), key="dropdown_object")],
    [sg.Button("Add to Query", key="add_to_query_button"), sg.Button("Execute", key="query_button")],
    [sg.Text("Query Result:")],
    [sg.Multiline("", size=(50, 5), key="result_text")],
    [sg.Text("Input Text:")],
    [sg.Multiline("Hallo, ich bin ein Text. Ich stehe hier um die Funktion von NLP zu testen.", size=(50, 5), key="input_text")],
    [sg.Button("Process Text", key="process_button")],
    [sg.Text("Output:")],
    [sg.Multiline("", size=(50, 5), key="output_text")]
]

window = sg.Window("SPARQL Query & NLP GUI", layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == "query_button":
        execute_query()
    elif event == "process_button":
        process_text()
    elif event == "select_file_button":
        select_owl_file()
    elif event == "add_to_query_button":
        create_query()

window.close()