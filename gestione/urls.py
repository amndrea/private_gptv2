from django.urls import path
from .views import *


app_name = "gestione"

urlpatterns = [

    # URL at which I view the server's health status
    path('health/', health, name="health"),
    # URL to which I show the documents currently ingested
    path('list_ingest/', ingest_list, name="list_ingest"),

]