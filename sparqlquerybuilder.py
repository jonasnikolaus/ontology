import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from rdflib.plugins.sparql import prepareQuery


# Funktion zum Erstellen der SPARQL-Abfrage
def create_query():
    selected_values = [dropdown.get() for dropdown in dropdowns]
    query = ''
    if all(value == 'none' for value in selected_values):
        showinfo('Error', 'Please select at least one value.')
        return
    else:
        for i, value in enumerate(selected_values):
            if value != 'none':
                query += f'{value} '
            if (i + 1) % 3 == 0 or i == len(selected_values) - 1:
                if i != len(selected_values) - 1:
                    query += '.\n'
    
    query_text.delete('1.0', tk.END)
    query_text.insert(tk.END, f"PREFIX AI4PD: <http://www.semanticweb.org/gerschuetz/forcude/AI4PD:>\nselect * where {{\n{query}\n}}")
    

# Erstelle das Hauptfenster
window = tk.Tk()
window.title('SPARQL Query Builder')

# Erstelle die Dropdown-Menüs
variables = ['Filter1', 'Filter2', 'Filter3', 'Filter4', 'Filter5', 'Filter6']
dropdowns = []
for variable in variables:
    values = ['none', '?tool', 'AI4PD:partOf', 'AI4PD:RapidMiner', '?toolbox', 'rdf:type', 'AI4PD:Toolbox', '?model', 'AI4PD:implementsMethod', '?method']
    dropdown = ttk.Combobox(window, values=values, state='readonly')
    dropdown.current(0)
    dropdowns.append(dropdown)

# Erstelle den "Show" Button
show_button = ttk.Button(window, text='Show Query', command=create_query)

# Erstelle das Textfeld für die Query-Anzeige
query_text = tk.Text(window, height=10, width=50)


# Positioniere die UI-Elemente
for i in range(len(variables)):
    ttk.Label(window, text=variables[i]).grid(row=i, column=0, padx=10, pady=5)
    dropdowns[i].grid(row=i, column=1, padx=10, pady=5)

show_button.grid(row=len(variables), column=0, columnspan=2, padx=10, pady=5)
query_text.grid(row=len(variables)+1, column=0, columnspan=2, padx=10, pady=5)


# Starte die GUI-Schleife
window.mainloop()