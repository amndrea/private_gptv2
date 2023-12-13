from django.urls import path
from .views import *


app_name = "gestione"

urlpatterns = [
    # URL to which I show the documents currently ingested
    path('list_ingest/', ingest_list, name="list_ingest"),

    path('health/', health, name="health")
]