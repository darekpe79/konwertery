import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF  # Import przestrzeni nazw RDF


# Funkcja wczytująca plik Excel pozostaje bez zmian
def handle_uploaded_excel(excel_file):
    df = pd.read_excel(excel_file)
    return df

# Zmodyfikowana funkcja generująca graf RDF
def generate_rdf(df, column_mapping):
    g = Graph()
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")

    for index, row in df.iterrows():
        # Upewniamy się, że 'concept' jest kluczem w 'column_mapping'
        if 'concept' in column_mapping and pd.notna(row[column_mapping['concept']]):
            # Tworzymy URIRef dla konceptu
            concept_uri = URIRef(row[column_mapping['concept']])
            # Dodajemy deklarację typu dla konceptu
            g.add((concept_uri, RDF.type, skos.Concept))

            # Iterujemy przez inne właściwości, jeśli istnieją
            for skos_property, column_name in column_mapping.items():
                if skos_property != 'concept' and column_name in df.columns and pd.notna(row[column_name]):
                    values = str(row[column_name]).split(',')
                    for value in values:
                        value = value.strip()
                        lang_tag = None
                        if '@' in value:
                            value, lang_tag = value.rsplit('@', 1)
                        property_name = skos_property  # Zakładamy, że przedrostka 'skos:' już nie ma
                        if property_name in ['broadMatch', 'narrowMatch', 'relatedMatch', 'closeMatch', 'exactMatch']:
                            g.add((concept_uri, skos[property_name], URIRef(value.strip())))
                        else:
                            if lang_tag:
                                g.add((concept_uri, skos[property_name], Literal(value.strip(), lang=lang_tag)))
                            else:
                                g.add((concept_uri, skos[property_name], Literal(value.strip())))
    return g
