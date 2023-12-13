from django.shortcuts import render
import json
import requests
import os

# ************************************************************************ #
# privateGPT server URL
HALFURL = "http://10.1.1.109:8001/v1/"
# ************************************************************************ #



# ********************************************************************************** #
#                     SUPPORT METHODS FOR VIEWS
# ********************************************************************************** #

# ----------------------------------------------------------------------- #
# Function that returns all the ingested documents in JSON format
# ----------------------------------------------------------------------- #
def json_documenti():
    URL = HALFURL + "ingest/list"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(e)

# ----------------------------------------------------------------------- #
# Function that show the actual health of E-ListaGPT server
# ----------------------------------------------------------------------- #
def health(request):
    URL = "http://10.1.1.109:8001/health"
    headers = {'Accept': 'application/json'}
    response = requests.get(URL, headers=headers)
    print(response)
    return render(request, 'gestione/health.html')

# ----------------------------------------------------------------------- #
# Function that given all the ingested documents in JSON format,
# show it in html
# ----------------------------------------------------------------------- #
def ingest_list(request):
    data = json_documenti()
    doc_info_list = [{"doc_id": doc["doc_id"], "file_name": doc["doc_metadata"]["file_name"]} for doc in data["data"]]

    nomi_file = set(doc["file_name"] for doc in doc_info_list)
    context = {"documenti": nomi_file}
    return render(request, template_name="gestione/list_ingest.html", context=context)



