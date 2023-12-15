from django.urls import path
from pip._internal.commands import completion

from .views import *


app_name = "gestione"

urlpatterns = [

    # URL at which I view the server's health status
    path('health/', health, name="health"),
    # URL to which I show the documents currently ingested
    path('list_ingest/', ingest_list, name="list_ingest"),



    # URL for completion retrival
    path('completion/', completion, name="completion"),

    # URL for chunks retrival
    path('chunks/', chunks, name="chunks"),

]