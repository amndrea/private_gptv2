from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
from gestione.models import *
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

def answers_list(user):
    """
    function that returns the last 5 answers given by the LLM to the user
    :param user: user that made the request
    :return: a list of answers
    """
    answers = Answer.objects.filter(user=user).order_by('-date')[:5]
    return answers


def doc_retrival_response_list(user):
    """
    Function that, given a user, returns the last 5 document retriva
    requests and the related responses
    :param user:User who made the request
    :return: document_request and related document_response, the most relevant part of
    ingested document
    """

    docs_request = DocRetrivalRequest.objects.filter(user=user).order_by('-date')[:5]
    ids_docs_request = [docs_request.id for docs_request in docs_request]
    docs_response = DocRetrivalResponse.objects.filter(doc_request__in=ids_docs_request)
    return docs_request, docs_response



def create_answer(user_request, response, user, doc_id=None, file_name=None):
    """
    function to create a response given by the LLM and save it in the DB
    :param user_request: user question
    :param response: LLM response
    :param user: user that made the request
    :param doc_id: id of the most relevant document used to generate the response
    :param file_name: name of the most relevant document used to generate the response
    :return: None, at the end of the function a new object is created
    """

    answer = Answer()
    answer.user_request = user_request
    answer.answer = response
    answer.user = user
    answer.doc_id = doc_id
    answer.file_name = file_name
    answer.save()


# ----------------------------------------------------------------------- #
#      functions to save a document retrival request and response
# ----------------------------------------------------------------------- #
def create_doc_retrival_request(user_request, user):
    doc_retrival_request = DocRetrivalRequest()
    doc_retrival_request.user_request = user_request
    doc_retrival_request.user = user
    doc_retrival_request.save()
    return doc_retrival_request


def create_doc_retrival_response(doc_retrival_request, text, score, file_name, doc_id):
    doc_retrival_response = DocRetrivalResponse()
    doc_retrival_response.doc_request = doc_retrival_request
    doc_retrival_response.text = text
    doc_retrival_response.score = score
    doc_retrival_response.file_name = file_name
    doc_retrival_response.doc_id = doc_id
    doc_retrival_response.save()
    return doc_retrival_response


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


# -------------------------------------------------------------------------------- #
# Method for completion retrival, if the request method is get, this function
# redirect to chat template
# -------------------------------------------------------------------------------- #
@execution_time
def chunks(request):

    # I show the user's last 5 messages in the template
    doc_request, doc_answers = doc_retrival_response_list(request.user)
    context = {"doc_requests": doc_request,
               "doc_answers": doc_answers,
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
            doc_request = create_doc_retrival_request(user_request, request.user)
            count = 0
            for choice in result["data"]:
                text = choice["text"]
                score = choice["score"]
                file_name = choice['document']['doc_metadata']['file_name']
                doc_id = choice['document']['doc_metadata']['doc_id']

                create_doc_retrival_response(doc_request, text, score, file_name, doc_id)
                count = count + 1
                if count == 5:
                    break
            return redirect('gestione:chunks', permanent=False)
        else:
            return JsonResponse({'error': 'Errore nella chiamata API'}, status=500)
