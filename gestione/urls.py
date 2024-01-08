from django.urls import path

from .views import *


app_name = "gestione"

urlpatterns = [

    # URL at which I view the server's health status
    path('health/', health, name="health"),

    # URL for upload document
    path('upload/', upload, name="upload"),
    path('check_upload/<int:session>/<file_not_supported>/', check_upload, name="check_upload"),

    # URl for delete a doc that already exists, not an ingested Doc
    path('cancel_doc/<int:file_pk>/<int:session_pk>/', cancel_file_object, name="cancel_doc"),

    # URl for modify the name of file and ingest it again if file already exists
    path('edit_file_name/<int:file_pk>/', edit_file_name, name="edit_file_name"),

    # URL to which I show the documents currently ingested
    path('list_ingest/', ingest_list, name="list_ingest"),

    # URL for delete a ingested document
    path('delete_doc/<str:file_name>/', delete_doc, name="delete_doc"),



    # URL for completion retrival
    path('completion/', completion, name="completion"),
    # URL for chunks retrival
    path('chunks/', chunks, name="chunks"),


]