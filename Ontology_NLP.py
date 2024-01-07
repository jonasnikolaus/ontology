# Importieren der notwendigen Bibliotheken
import spacy  # für NLP
import difflib  # zum Finden ähnlicher Wörter
from rdflib import Graph, Namespace  # zum Arbeiten mit RDF-Graphen
from rdflib.plugins.sparql import prepareQuery  # zum Vorbereiten von SPARQL-Abfragen
import PySimpleGUI as sg  # für die GUI
import os  # für Dateioperationen
import requests  # für HTTP-Anfragen (z.B. API-Aufrufe)
import re # für das aufteilen am String "und"

# Funktion, um den spezifischen Teil des AI4PD-Namespace aus einem String zu extrahieren
def extract_ai4pd_part(item):
    # Teilt den String am "AI4PD:" auf
    parts = item.split('AI4PD:')
    if len(parts) == 2:
        # Gibt den zweiten Teil zurück
        return 'AI4PD:' + parts[1]
    else:
        return None

# Funktion, um eindeutige Subjekte aus einem RDF-Graphen abzurufen
def get_unique_subjects(graph):
    # Vorbereitung der SPARQL-Abfrage
    query = prepareQuery("SELECT DISTINCT ?s WHERE {?s ?p ?o}")
    # Ausführung der SPARQL-Abfrage
    results = graph.query(query)
    # Extrahieren der eindeutigen Subjekte und Sortieren der Liste
    unique_subjects = [str(result[0]) for result in results]
    return sorted([extract_ai4pd_part(item) for item in unique_subjects if 'AI4PD:' in item])

# Funktion, um eindeutige Prädikate aus einem RDF-Graphen abzurufen
def get_unique_predicates(graph):
    # Ähnlich wie get_unique_subjects, aber für Prädikate
    query = prepareQuery("SELECT DISTINCT ?p WHERE {?s ?p ?o}")
    results = graph.query(query)
    unique_predicates = [str(result[0]) for result in results]
    return sorted([extract_ai4pd_part(item) for item in unique_predicates if 'AI4PD:' in item])

# Funktion, um eindeutige Objekte aus einem RDF-Graphen abzurufen
def get_unique_objects(graph):
    # Ähnlich wie get_unique_subjects, aber für Objekte
    query = prepareQuery("SELECT DISTINCT ?o WHERE {?s ?p ?o}")
    results = graph.query(query)
    unique_objects = [str(result[0]) for result in results]
    return sorted([extract_ai4pd_part(item) for item in unique_objects if 'AI4PD:' in item])

# Funktion, um die nähesten Werte aus den Dropdown-Menüs zu finden und den nähesten zurückzugeben
def find_closest_match(token, choices, replace):
    # Verwendet die difflib-Bibliothek, um den ähnlichsten String zu finden
    match = difflib.get_close_matches(token, choices, n=1, cutoff=0.5) # 0.5 ist die Mindestübereinstimmung
    if match:
        return match[0]
    # Wenn kein Match gefunden wird, wird der Originalwert zurückgegeben
    return replace

# Funktion, um eine SPARQL-Abfrage aus den NLP-Eingaben zu generieren
def nlp_query(matched_subjects, matched_predicates, matched_objects):
    # Diese Funktion nimmt die Matches aus der NLP-Analyse und baut daraus eine SPARQL-Abfrage auf
    query_parts = []
    for subject, predicate, object_ in zip(matched_subjects, matched_predicates, matched_objects):
        query_part = ''
        # Wenn ein Subjekt erkannt wurde, wird es zur Abfrage hinzugefügt
        if subject:
            query_part += f'{subject} '
        # Gleiches gilt für Prädikate
        if predicate:
            query_part += f'{predicate} '
        # Und Objekte
        if object_:
            query_part += f'{object_} '
        
        query_part += '.' + "\n" # Ein Punkt markiert das Ende eines Tripels in SPARQL, Hinzufügen neuer Zeile
        query_parts.append(query_part)

    # Hier wird die aktuelle Abfrage aus dem GUI-Feld übernommen
    current_query = values['query_text'].strip()
    # Auch das "Select"-Feld wird ausgelesen
    select_value = values['input_select'].strip()
    # Das Sternchen (*) wird durch den Wert im "Select"-Feld ersetzt
    current_query = current_query.replace("select *", f"select {select_value}")

    # Die neuen Abfrageteile werden zur bestehenden Abfrage hinzugefügt
    if "}" in current_query:
        current_query = current_query.rsplit("}", 1)[0]  + '\n'.join(query_parts) + "\n}"
    else:
        current_query += f"PREFIX AI4PD: <http://www.semanticweb.org/gerschuetz/forcude/AI4PD:>\nselect * where {{\n{' '.join(query_parts)}}}"
    
    # Das Abfragefeld im GUI wird aktualisiert
    window['query_text'].update(current_query)

# Funktion, um die SPARQL-Abfrage auszuführen und das Ergebnis im Textbereich anzuzeigen
def execute_query():
    try:
         # Die aktuelle Abfrage wird ausgelesen
        query = values['query_text'].strip()
        # Die SPARQL-Abfrage wird ausgeführt
        results = graph.query(query)
        # Vorbereitung der Ergebnistexte
        result_texts = []
        for result in results:
            # Extrahieren des relevanten Teils des Ergebnis-Strings
            result_text = str(result[0])
            extracted_part = extract_ai4pd_part(result_text)
            # Fügen Sie nur den extrahierten Teil zur Ergebnisliste hinzu, falls vorhanden
            if extracted_part:
                result_texts.append(extracted_part)

        # Wenn keine Ergebnisse gefunden wurden
        if not result_texts:
            result_texts.append("Keine Ergebnisse gefunden.")
        # Update des Ergebnisfeldes im GUI
        window['result_text'].update('\n'.join(result_texts))
    # Bei einem Fehler wird die Fehlermeldung im Ergebnisbereich ausgegeben
    except Exception as e:
        window['result_text'].update(f"Fehler: {str(e)}")

# API-Aufruf an OpenThesaurus, um Synonyme für "word" zu erhalten
def call_open_thesaurus_api(word):
    synonyms = set()
    try:
        # Ein API-Aufruf wird getätigt, um die Synonyme für das Wort zu erhalten
        response = requests.get(f"https://www.openthesaurus.de/synonyme/search?q={word}&format=application/json")
        data = response.json()
        for meaning in data.get('synsets', []):
            for term in meaning.get('terms', []):
                synonyms.add(term['term'])
    except Exception as e:
        # Fehlermeldung, falls der API-Aufruf fehlschlägt
        print(f"Error while querying OpenThesaurus: {e}")
    print(f"Synonyms fetched from OpenThesaurus for '{word}': {synonyms}")
    return list(synonyms)

# Synonyme für die Ersetzung werden hier festgelegt
hard_coded_synonyms = {
    "teil": "partof",
    "eine": "a",
    "ein":"a",
    # Weitere Synonyme hier hinzufügen
}

# Funktion zum Auffinden und Ersetzen von Synonymen in einer Liste von Wörtern
def find_and_replace_synonyms(word_list):
    for word in word_list:
        # Synonyme von OpenThesaurus werden abgerufen
        synonyms = call_open_thesaurus_api(word)
        
        # Das ursprüngliche Wort wird für den Vergleich hinzugefügt
        synonyms.append(word)
        
        # Überprüfung, ob eines der Synonyme in der fest codierten Liste ist
        for synonym in synonyms:
            if synonym.lower() in hard_coded_synonyms:
                # Ersetzt das Wort in der Liste durch das fest codierte Synonym
                print(f"Matched '{synonym}' with hard-coded synonym: {hard_coded_synonyms[synonym.lower()]}")
                index = word_list.index(word)
                word_list[index] = hard_coded_synonyms[synonym.lower()]
                break

# Funktion, um den eingegebenen Text mit NLP zu interpretieren und zu verarbeiten
def process_text():

    # Auslesen der aktuellen Werte aus dem Fenster
    current_values = window.read()[1]  

    # Aufteilen des eingegebenen Texts in Segmente, getrennt durch "&"
    #segments = current_values['input_text'].strip().lower().split('&')
    segments = re.split(r'&|\bund\b', current_values['input_text'].strip().lower())


    # Listen zur Speicherung der erkannten Subjekte, Prädikate und Objekte für die spätere Erstellung der Query
    matched_subjects = []
    matched_predicates = []
    matched_objects = []
    
    for segment in segments:
        text = segment.strip()
        tokens = text.split()
        
        # Aufruf der Funktion zur Ersetzung von Synonymen
        find_and_replace_synonyms(tokens) 

        # Debug-Ausgabe
        print("Debug: Tokens nach Synonym-Ersetzung:", tokens)  

        # Optionen aus den Dropdown-Menüs im GUI
        subjects = list(window['dropdown_subject'].Values)
        predicates = list(window['dropdown_predicate'].Values)
        objects = list(window['dropdown_object'].Values)

        # Finden der am besten passenden Übereinstimmungen für jedes Token. Wenn keines gefunden wird, wird der eingegebene Wert übernommen.
        subject_match = find_closest_match(tokens[0], subjects, tokens[0]) if len(tokens) > 0 else None
        predicate_match = find_closest_match(tokens[1], predicates, tokens[1]) if len(tokens) > 1 else None
        object_match = find_closest_match(tokens[2], objects, tokens[2]) if len(tokens) > 2 else None

        # Speichern der erkannten Werte für die spätere Erstellung der SPARQL-Abfrage
        matched_subjects.append(subject_match)
        matched_predicates.append(predicate_match)
        matched_objects.append(object_match)

    # Aufbau des Query-Strings mit den gesammelten matched_subjects, matched_predicates und matched_objects
    query_parts = []
    for subject, predicate, object_ in zip(matched_subjects, matched_predicates, matched_objects):
        query_part = ''
        if subject:
            query_part += f'{subject} '
        if predicate:
            query_part += f'{predicate} '
        if object_:
            query_part += f'{object_} '
        
        query_part += '.'
        query_parts.append(query_part)

    current_query = values['query_text'].strip()
    select_value = values['input_select'].strip()
    current_query = current_query.replace("select *", f"select {select_value}")

    if "}" in current_query:
          current_query = current_query.replace("}", f"{query_part}}}")
    else:
        current_query += f"PREFIX AI4PD: <http://www.semanticweb.org/gerschuetz/forcude/AI4PD:>\nselect * where {{\n{' '.join(query_parts)}}}"
        
    # Teilquerys werden automatisch hinzugefügt
    nlp_query(matched_subjects, matched_predicates, matched_objects)

    #Informationen zu NLP, Tokens, Wortarten, etc.
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

# Funktion, um eine OWL-Datei auszuwählen und die Dropdown-Menüs mit eindeutigen Subjekten, Prädikaten und Objekten zu füllen
def select_owl_file():
    global graph
    global owl_file_path # Globale Variable für den Dateipfad
    owl_file_path = sg.popup_get_file('Select OWL File', file_types=(("OWL Files", "*.owl"),))
    if owl_file_path:
        # Aktualisierung des Labels für die ausgewählte Datei
        file_name = os.path.basename(owl_file_path)
        window['selected_file_label'].update("Selected File: " + file_name)
        
        # Einlesen der OWL-Datei und Auffüllen der Dropdowns
        graph = Graph()
        graph.parse(owl_file_path)
        unique_subjects = get_unique_subjects(graph)
        unique_predicates = get_unique_predicates(graph)
        unique_objects = get_unique_objects(graph)
        window['dropdown_subject'].update(values=unique_subjects, value='')
        window['dropdown_predicate'].update(values=unique_predicates, value='')
        window['dropdown_object'].update(values=unique_objects, value='')
    else:
        owl_file_path = ""
        window['selected_file_label'].update("No File Selected")

# Funktion, um den aktuellen Inhalt der Dropdown-Menüs zur Abfrage hinzuzufügen
def create_query():
    # Auslesen der ausgewählten Werte aus den Dropdown-Menüs
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
                query_part += '.\n'  # Ein Punkt und ein Zeilenumbruch am Ende jedes Tripels
    
    # Aktualisierung des Abfragefelds im GUI
    current_query = values['query_text'].strip()
    select_value = values['input_select'].strip()
    current_query = current_query.replace("select *", f"select {select_value}")

    # Hinzufügen des neuen Abfrageteils zur bestehenden Abfrage
    if "}" in current_query:
        current_query = current_query.replace("}", f"{query_part}}}")
    else:
        current_query += f"PREFIX AI4PD: <http://www.semanticweb.org/gerschuetz/forcude/AI4PD:>\nselect * where {{\n{query_part}}}"
    window['query_text'].update(current_query)

    # Zurücksetzen der Dropdowns
    window['dropdown_subject'].update(value='')
    window['dropdown_predicate'].update(value='')
    window['dropdown_object'].update(value='')

# Initialisierung des NLP-Modells
nlp = spacy.load("de_core_news_sm")

# Definition des GUI-Layouts
layout = [
    # Textfeld für die SPARQL-Abfrage
    [sg.Text("SPARQL Query:")],
    [sg.Multiline("", size=(50, 10), key="query_text")],
    # Button für die Auswahl einer OWL-Datei
    [sg.Button("Select OWL File", key="select_file_button")],
    [sg.Text("No File Selected", size=(40, 1), key="selected_file_label")],
    # Eingabefeld für das SELECT-Statement in SPARQL
    [sg.Text("Select:"), sg.InputText("*", size=(40, 1), key="input_select")],
    # Dropdown-Menüs für Subjekte, Prädikate und Objekte
    [sg.Text("Subject:"), sg.Combo([], size=(40, 1), key="dropdown_subject", enable_events=True)],
    [sg.Text("Predicate:"), sg.Combo([], size=(40, 1), key="dropdown_predicate", enable_events=True)],
    [sg.Text("Object:"), sg.Combo([], size=(40, 1), key="dropdown_object", enable_events=True)],
    # Buttons für die Abfrageausführung und zum Hinzufügen zur Abfrage
    [sg.Button("Add to Query", key="add_to_query_button"), sg.Button("Execute", key="query_button")],
    # Textfeld für die Ergebnisse der Abfrage
    [sg.Text("Query Result:")],
    # Textfeld für die NLP-Eingabe
    [sg.Multiline("", size=(50, 5), key="result_text")],
    [sg.Text("Input Text:")],
    [sg.Multiline("?individual Bestandteil Developmentteam und ?individual eine person", size=(50, 5), key="input_text")],
    # Button für die Verarbeitung des Texts
    [sg.Button("Process Text", key="process_button")],
    # Textfeld für die NLP-Ausgabe
    [sg.Text("Output:")],
    [sg.Multiline("", size=(50, 5), key="output_text")]
]

# Haupt-GUI-Loop
window = sg.Window("SPARQL Query & NLP GUI", layout)

while True:
    event, values = window.read()

    # Schließen des Fensters
    if event == sg.WINDOW_CLOSED:
        break
    # Ausführen der SPARQL-Abfrage
    elif event == "query_button":
        execute_query()
    # Verarbeiten des Textes mit NLP    
    elif event == "process_button":
        process_text()
    # Auswählen der OWL-Datei 
    elif event == "select_file_button":
        select_owl_file()
    # Hinzufügen zur SPARQL-Abfrage
    elif event == "add_to_query_button":
        create_query()

# Schließen des Fensters und Beenden der Anwendung
window.close()