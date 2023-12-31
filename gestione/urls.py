from django.urls import path
from .views import *

app_name = "gestione"


urlpatterns = [

    # URL at which I view the server's health status
    path('health/', health, name="health"),

    # URL for upload document
    path('upload/', upload, name="upload"),

    # URL where I view the results of the current ingestion session
    path('check_upload/<int:session>/<file_not_supported>/', check_upload, name="check_upload"),

    # URl for delete a doc that already exists, not an ingested Doc
    path('cancel_doc/<int:file_pk>/<int:session_pk>/', cancel_file_object, name="cancel_doc"),

    # URl for modify the name of file and ingest it again if file already exists
    path('edit_file_name/<int:file_pk>/', edit_file_name, name="edit_file_name"),

    # URL with which to replace a corrupted file with the current one
    path('replace_file/<int:file_pk>/', replace_file, name="replace_file"),

    # URL to which I show the documents currently ingested
    path('list_ingest/', ingest_list, name="list_ingest"),

    # URL for delete a ingested document
    path('delete_doc/<str:file_name>/', delete_document_view, name="delete_doc"),

    # URL for completion retrival
    path('completion/', completion, name="completion"),

    # URL for chunks retrival
    path('chunks/', chunks, name="chunks"),

    # URL for create a question for admin for revision
    path('create_question/<int:answer_pk>/<int:satisfied>/', create_question, name="create_question"),

    # URL for show all question by one type
    path('list_question/',QuestionList.as_view(), name="list_question"),


    # URL al quale l'admin visualizza una risposta nello specifico e decide se approvarla o no
    #path('visualizza_domanda/<int:domanda_pk>/<int:stato>/', visualizza_domanda, name="visualizza_domanda"),

]
