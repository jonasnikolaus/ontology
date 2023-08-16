import tkinter as tk
import spacy

def process_text():
    text = input_text.get("1.0", tk.END).strip()
    if text:
        doc = nlp(text)
        
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

# Initialisiere Spacy mit dem gewünschten Sprachmodell
nlp = spacy.load("de_core_news_sm")

# Erstelle das Hauptfenster
window = tk.Tk()
window.title("NLP GUI")

# Eingabetextfeld
input_text = tk.Text(window, height=10, width=50)
input_text.pack()

# Verarbeitungsbutton
process_button = tk.Button(window, text="Verarbeite Text", command=process_text)
process_button.pack()

# Ausgabetextfeld
output_text = tk.Text(window, height=20, width=50)
output_text.pack()

# Starte die GUI-Schleife
window.mainloop()
