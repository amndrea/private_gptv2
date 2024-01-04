from django.urls import path

from .views import *


app_name = "gestione"

urlpatterns = [

    # URL at which I view the server's health status
    path('health/', health, name="health"),

    # URL for upload document
    path('upload/', upload, name="upload"),

    # URL to which I show the documents currently ingested
    path('list_ingest/', ingest_list, name="list_ingest"),

    # URL for delete a document
    path('delete_doc/<str:file_name>/', delete_doc, name="delete_doc"),

    # URL for completion retrival
    path('completion/', completion, name="completion"),
    # URL for chunks retrival
    path('chunks/', chunks, name="chunks"),

]