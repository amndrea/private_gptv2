import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
from gestione.models import Answer
import time

# ************************************************************************ #
# privateGPT server URL
HALFURL = "http://10.1.1.109:8001/v1/"
# ************************************************************************ #


# --------------------------------------------------------------------------------------- #
# function that calculates the execution time of the function passed as a parameter
# --------------------------------------------------------------------------------------- #
def execution_time(function):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        time_taken = end_time - start_time
        print(f'function {function.__name__} took {time_taken}')
        return result
    return wrapper


# ********************************************************************************** #
# ********************************************************************************** #
#                     SUPPORT METHODS FOR VIEWS
# ********************************************************************************** #
# ********************************************************************************** #


# ----------------------------------------------------------------------- #
#         function that returns the last 5 messages from a user
# ----------------------------------------------------------------------- #
def answers_list(user):
    answers = Answer.objects.filter(user=user).order_by('-date')[:5]
    return answers


# ----------------------------------------------------------------------- #
#          function to save a chat response to the database
# ----------------------------------------------------------------------- #
def create_answer(user_request, response, user, doc_id=None, file_name=None):
    answer = Answer()
    answer.user_request = user_request
    answer.answer = response
    answer.user = user
    answer.doc_id = doc_id
    answer.file_name = file_name
    answer.save()


# ----------------------------------------------------------------------- #
#     Function that returns all the ingested documents in JSON format
# ----------------------------------------------------------------------- #
def json_documenti():
    url = HALFURL + "ingest/list"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(e)


# ----------------------------------------------------------------------- #
#     Function for extract data from response of chunks
# ----------------------------------------------------------------------- #
def json_document_chunks(result, what): # anche parametro what per capire cosa recuperare
    data_list = result.get("data", [])
    result = []

    for item in data_list:
        if item.get("object") == "context.chunk":
            score = item.get("score")
            document_data = item.get("document", {})
            text = item.get("text")

            if score < 0.7:
                continue
            else:
                if document_data.get("object") == "ingest.document":
                    doc_id = document_data.get("doc_id")
                    file_name = document_data.get("doc_metadata", {}).get("file_name")
                    original_text = document_data.get("original_text")

                    #print("Score:", score)
                    #print("Text:", text)
                    #print("Doc ID:", doc_id)
                    #print("File Name:", file_name)
                    #print("Original Text:", original_text)
                    if what == 1:
                        result.append(doc_id)
                    else:
                        result.append((file_name, text))

    return result
# ********************************************************************************** #
# ********************************************************************************** #
#                                API FOR PRIVATEGPT
# ********************************************************************************** #
# ********************************************************************************** #


# ----------------------------------------------------------------------- #
# Function that show the actual health of E-ListaGPT server
# ----------------------------------------------------------------------- #
def health(request):
    url = "http://10.1.1.109:8001/health"
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    status = response.status_code
    return render(request, template_name='gestione/health.html', context={'status': status})


# ----------------------------------------------------------------------- #
# Function that given all the ingested documents in JSON format,
# show it in html template
# ----------------------------------------------------------------------- #
def ingest_list(request):
    data = json_documenti()
    doc_info_list = [{"doc_id": doc["doc_id"], "file_name": doc["doc_metadata"]["file_name"]} for doc in data["data"]]

    nomi_file = set(doc["file_name"] for doc in doc_info_list)
    context = {"documenti": nomi_file}
    return render(request, template_name="gestione/list_ingest.html", context=context)




# -------------------------------------------------------------------------------- #
# Method for completion retrival, if the request method is get, this function
# redirect to chat template
# -------------------------------------------------------------------------------- #
@execution_time
def completion(request):
    # I show the user's last 5 messages in the template
    answers = answers_list(request.user)
    context = {
        "answers": answers,
        "type": 'completion'
    }

    # shows the chat template
    if request.method == 'GET':
        return render(request, template_name='gestione/elisa.html', context=context)

    elif request.method == 'POST':
        user_request = request.POST.get('questions')
        api_url = HALFURL + 'completions'

        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        payload = {
            'prompt': user_request,
            'system_prompt': 'talk to me on italian, your name is Elisa ',
            'use_context': 'true'

        }
        response = requests.post(api_url, headers=headers, json=payload)

        # If the response was successful I create an Answer object and display it in the template
        # and render the template with a GET to continue

        if response.status_code == 200:
            result = response.json()

            first_result = result["choices"][0]
            content_response = first_result["message"]["content"]
            doc_id = first_result["sources"][0]["document"]["doc_id"]
            file_name = first_result["sources"][0]["document"]["doc_metadata"]["file_name"]
            create_answer(user_request, content_response, request.user, doc_id=doc_id, file_name=file_name)

            return redirect('gestione:completion', permanent=False)
        else:
            return JsonResponse({'error': 'Errore nella chiamata API'}, status=500)

@execution_time
def chunks(request):
    # I show the user's last 5 messages in the template
    answers = answers_list(request.user)
    context = {"answers": answers,
               "type": 'chunks'
               }
    # shows the chat template
    if request.method == 'GET':
        return render(request, template_name='gestione/elisa.html', context=context)

    elif request.method == 'POST':
        user_request = request.POST.get('questions')
        api_url = HALFURL + 'chunks'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        payload = {
            'text': user_request,
            'system_prompt': 'talk to me on italian, your name is Elisa ',
        }
        response = requests.post(api_url, headers=headers, json=payload)

        # If the response was successful I create an Answer object and display it in the template
        # and render the template with a GET to continue
        if response.status_code == 200:
            result = response.json()
            # call extraction data from json for render in a template the most relevant document
            data_form_doc = json_document_chunks(result, 2)
            print(data_form_doc)



            #result = response.json()
            #first_result = result["choices"][0]
            #content_response = first_result["message"]["content"]
            #doc_id = first_result["sources"][0]["document"]["doc_id"]
            #file_name = first_result["sources"][0]["document"]["doc_metadata"]["file_name"]

            #create_answer(user_request, content_response, request.user, doc_id=doc_id, file_name=file_name)

            #return redirect('gestione:chunks', permanent=False)
            return JsonResponse({'result': result})
        else:
            return JsonResponse({'error': 'Errore nella chiamata API'}, status=500)
