import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from tempfile import NamedTemporaryFile
from .forms import ColumnMappingForm
from .utils import handle_uploaded_excel, generate_rdf
from .skos_properties import SKOS_PROPERTIES

def upload_excel(request):
    if request.method == 'POST':
        form = ColumnMappingForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            # Zmodyfikuj, aby pominąć klucze, które nie zostały wypełnione
            column_mapping = {
                prop: form.cleaned_data.get(prop) for prop in SKOS_PROPERTIES
                if form.cleaned_data.get(prop) is not None
            }

            # Wywołujemy 'handle_uploaded_excel' tylko z plikiem Excel
            df = handle_uploaded_excel(excel_file)
            # Teraz przekazujemy 'df' i 'column_mapping' do funkcji 'generate_rdf'
            rdf_graph = generate_rdf(df, column_mapping)

            format = form.cleaned_data['output_format']

            tmp_file_path = None
            try:
                with NamedTemporaryFile(delete=False, suffix=f'.{format}', dir=settings.MEDIA_ROOT) as tmp_file:
                    rdf_graph.serialize(destination=tmp_file.name, format=format)
                    tmp_file_path = tmp_file.name

                with open(tmp_file_path, 'rb') as tmp_file:
                    response = HttpResponse(tmp_file.read(), content_type="application/rdf+xml")
                    rdf_filename = f"rdf_data.{format}"
                    response['Content-Disposition'] = f'attachment; filename={rdf_filename}'
                    return response
            finally:
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
    else:
        form = ColumnMappingForm()

    return render(request, 'upload.html', {'form': form})
