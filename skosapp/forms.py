from django import forms
from django.core.exceptions import ValidationError
import pandas as pd
from .skos_properties import SKOS_PROPERTIES

class ColumnMappingForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload your Excel file with the SKOS data.'
    )
    output_format = forms.ChoiceField(
        choices=[
            ('xml', 'XML'),
            ('turtle', 'Turtle'),
            ('n3', 'N3'),
            ('nt', 'NT'),
            ('pretty-xml', 'Pretty XML'),
            ('trix', 'TriX'),
            ('trig', 'TriG')
        ],
        label='Output Format',
        help_text='Select the RDF serialization format for the output file.'
    )

    # Dynamically add a field for each SKOS property
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for prop in SKOS_PROPERTIES:
            self.fields[prop] = forms.CharField(
                required=False,
                label=f'skos:{prop}',
                help_text=f'Enter the column name from the Excel sheet for the skos:{prop} property.'
            )

    def clean(self):
        cleaned_data = super().clean()
        excel_file = cleaned_data.get('excel_file')

        if excel_file:
            try:
                df = pd.read_excel(excel_file)
            except Exception as e:
                raise ValidationError(f"Error reading excel file: {e}")

            excel_columns = df.columns.tolist()

            for prop in SKOS_PROPERTIES:
                column_name = cleaned_data.get(prop)
                if column_name and column_name not in excel_columns:
                    self.add_error(prop, ValidationError(f"Column '{column_name}' does not exist in the excel file."))

        return cleaned_data

# Gdzie SKOS_PROPERTIES to lista lub tupla nazw właściwości SKOS
# skos_properties.py
