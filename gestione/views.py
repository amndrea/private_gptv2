from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView

from gestione.models import *
from .forms import InsertQuestionForm
from docx import Document
from odf import text, teletype
from odf.opendocument import load

import time
import os
import magic
import re
import requests
import PyPDF2


# ************************************************************************ #
#                      privateGPT server URL
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


def create_doc_retrival_response(doc_retrival_request, texts, score, file_name, doc_id):
    doc_retrival_response = DocRetrivalResponse()
    doc_retrival_response.doc_request = doc_retrival_request
    doc_retrival_response.text = texts
    doc_retrival_response.score = score
    doc_retrival_response.file_name = file_name
    doc_retrival_response.doc_id = doc_id
    doc_retrival_response.save()
    return doc_retrival_response


# ----------------------------------------------------------------------- #
#             function to save an infested document
# ----------------------------------------------------------------------- #
def create_ingested_file(user, file):
    ingested_file = IngestedFile()
    ingested_file.user = user
    ingested_file.file = file
    ingested_file.save()
    return ingested_file


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
#  Function that checks whether a document with this name already exists
# ----------------------------------------------------------------------- #
def already_exist(new_file_name):
    data = json_documenti()
    doc_info_list = [{"doc_id": doc["doc_id"], "file_name": doc["doc_metadata"]["file_name"]} for doc in data["data"]]
    file_names = set(doc["file_name"] for doc in doc_info_list)
    for file_name in file_names:
        if file_name == new_file_name:
            return True
    return False


# ------------------------------------------------------------------------------------------ #
# Function fot control il one file is on supported format, and if I need to preprocess it
# this function return
# 0 if the document is not supported
# 1 if the document is supported (textual)
# 2 if the document is Word format, it can be supported but need some preprocess operations
# 3 if the document is Excel format, it can be supported but need some preprocess operations
# ------------------------------------------------------------------------------------------ #
def supported_format_file(file_path):
    mime = magic.Magic()
    file_type = mime.from_file(file_path)

    if file_type == "ASCII text" or "Unicode text" in file_type or "UTF-8 text" in file_type:
        return 'text'
    if file_type == "OpenDocument Text":
        return 'opendocument'
    if file_type.startswith("Microsoft Word"):
        return 'word'
    if file_type == "OpenDocument Spreadsheet":
        return 'openspreadsheet'
    if file_type.startswith("Microsoft Excel"):
        return 'excel'
    if file_type.startswith("PDF document"):
        return 'pdf'
    return '1'


# ----------------------------------------------------------------------- #
# Function for extract information from .docx file
# This function take on input the path of word file and the directory
# of that file. It returns a path of textual file, with the same name
# of original file but .txt
# ----------------------------------------------------------------------- #
def convert_unsupported_word_file(file_path_source, dir_src, types):
    if types == "word":
        document = Document(file_path_source)
        extracted_text = ""
        for paragraph in document.paragraphs:
            extracted_text += paragraph.text + "\n"
    else:
        doc = load(file_path_source)
        extracted_text = ""
        for text_node in doc.getElementsByType(text.P):
            extracted_text += teletype.extractText(text_node)

    original_file_name = os.path.basename(file_path_source)
    with open(dir_src + original_file_name + ".txt", "w") as text_file:
        text_file.write(extracted_text)

    return text_file.name


def extract_text_from_pdf(pdf_path, dir_src):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extractText()
    original_file_name = os.path.basename(pdf_path)
    with open(dir_src + original_file_name + ".txt", "w") as text_file:
        text_file.write(text)

    return text_file.name



# @ TODO queste porcherie sono da implementare
def extract_text_from_excel(excel_path):
    pass
# ------------------------------------------------------------------------------------------ #
# Function that, given the name of a file, deletes all the chunks of that file
# from the ingested documents
# ------------------------------------------------------------------------------------------ #
def delete_document(file_name):
    data = json_documenti()
    doc_info_list = [{"doc_id": doc["doc_id"], "file_name": doc["doc_metadata"]["file_name"]} for doc in data["data"]]

    # list of chunks to delete
    doc_ids = []
    for doc_info in doc_info_list:
        if doc_info["file_name"] == file_name:
            doc_ids.append(doc_info["doc_id"])

    for doc_id in doc_ids:
        api_url = HALFURL + 'ingest/'
        api_url = api_url + str(doc_id)
        headers = {'Accept': 'application/json'}

        response = requests.delete(api_url, headers=headers)
        if response.status_code != 200:
            print("error during delete request")


# --------------------------------------------------------------------- #
# Funzione per ingestare un documento dato il path del documento
# La funzione è utile per creare documenti e ingestarli senza passare
# per la gui, quando una domanda viene approvata
# --------------------------------------------------------------------- #
def ingest_file(file_path):
    api_url = HALFURL + "ingest"
    headers = {'Accept': 'application/json'}
    files = {'file': open(file_path, 'rb')}
    response = requests.post(api_url, headers=headers, files=files)
    return response.status_code == 200

# ********************************************************************************** #
# ********************************************************************************** #
#                                API FOR PRIVATEGPT
# ********************************************************************************** #
# ********************************************************************************** #


# ----------------------------------------------------------------------- #
# Function that show the actual health of E-ListaGPT server
# ----------------------------------------------------------------------- #
# TODO gestire un try, cathc, nella pagina iniziale, se il server e down, dopo il login mostro questa porcheria
#   altrimenti proseguo con la home utente loggato, in generale nel template home utente loggato, se lo stato è
#      false anzi che fare render, visualizzo un errore e basta, altrimenti vado avanti con la home utente loggato
def health(request):
    try:
        url = "http://10.1.1.109:8001/health"
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        status = response.status_code
        return render(request, template_name='gestione/health.html', context={'status': status})
    except Exception as e:
        return render(request, template_name='gestione/health.html', context={'status': 0})



# TODO provare anche con la lista di messaggi

# TODO provare la funzione di ingestion di un semplice text per i messaggi generati correttamente
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
            'system_prompt': 'Talk only in Italian',
            'use_context': 'true'
        }
        response = requests.post(api_url, headers=headers, json=payload)

        # If the response was successful I create an Answer object and display it in the template
        # and render the template with a GET to continue

        if response.status_code == 200:
            result = response.json()

            first_result = result["choices"][0]
            content_response = first_result["message"]["content"]
            content_response = content_response.replace("```", "")
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
                texts = choice["text"]
                score = choice["score"]
                file_name = choice['document']['doc_metadata']['file_name']
                doc_id = choice['document']['doc_metadata']['doc_id']

                create_doc_retrival_response(doc_request, texts, score, file_name, doc_id)
                count = count + 1
                if count == 5:
                    break
            return redirect('gestione:chunks', permanent=False)
        else:
            return JsonResponse({'error': 'Errore nella chiamata API'}, status=500)


# ----------------------------------------------------------------------- #
# Function that given all the ingested documents in JSON format,
# show it in html template
# ----------------------------------------------------------------------- #
def ingest_list(request):
    data = json_documenti()
    doc_info_list = [{"doc_id": doc["doc_id"], "file_name": doc["doc_metadata"]["file_name"]} for doc in data["data"]]
    file_name = set(doc["file_name"] for doc in doc_info_list)
    context = {"documenti": file_name}
    return render(request, template_name="gestione/list_ingest.html", context=context)


# ----------------------------------------------------------------------- #
# View for delete all chunks given a name of an ingested document
# ----------------------------------------------------------------------- #
def delete_document_view(request, file_name):
    delete_document(file_name)
    return redirect('gestione:list_ingest')


# ----------------------------------------------------------------------- #
# Function for update file, if file already exist, the admin can
# if the file is already present, the admin can choose whether to replace
# the old file or keep both
# if the file format is not supported, an error message appears
# otherwise the file is converted if necessary and ingested
# ----------------------------------------------------------------------- #
def upload(request):
    if request.method == 'GET':
        return render(request, template_name="gestione/upload.html")

    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')

        # List of temporary file update from user
        saved_file_path = []

        # files split in 3 list, file ok. file not supported and file to modify before ingestion
        files_ok = []
        files_not_supported = []
        dir = os.getcwd()+"/file/"
        os.makedirs(dir, exist_ok=True)

        try:
            # Save the upload fine in a temporary directory
            for file in files:
                file_path = os.path.join(dir, file.name)
                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                saved_file_path.append(file_path)

            # Check if this file is supported file or not
            for file_path in saved_file_path:
                if supported_format_file(file_path) == '1':
                    files_not_supported.append(file_path)
                elif supported_format_file(file_path) == 'text':
                    files_ok.append(file_path)
                elif supported_format_file(file_path) == 'pdf':
                    file_text = extract_text_from_pdf(file_path,dir)
                    files_ok.append(file_text)
                elif supported_format_file(file_path) == 'opendocument':
                    file_text = convert_unsupported_word_file(file_path, dir, 'open')
                    files_ok.append(file_text)
                elif supported_format_file(file_path) == 'word':
                    file_text = convert_unsupported_word_file(file_path, dir, 'word')
                    files_ok.append(file_text)

                # TODO da implementare questa roba
                #  Excel document
                elif supported_format_file(file_path) == 3:
                    # TODO qui chiamo la funzione di modifica ed estrazione del contenuto dal file
                    print("trovato formato docx")

            # Only for good file check if already exists
            session = IngestionSession()
            session.save()
            for file_ok in files_ok:
                ing_file = IngestedFile()
                ing_file.user = request.user
                ing_file.file = file_ok
                ing_file.ingestion_session = session

                ing_file.file_name = os.path.basename(file_ok)
                if already_exist(ing_file.file_name):
                    ing_file.stato = "already exists"
                else:
                    if ingest_file(file_ok):
                        ing_file.stato = "ok"
                ing_file.save()
        finally:
            file_ingested = IngestedFile.objects.filter(ingestion_session=session).filter(stato='ok')
            for file in file_ingested:
                os.remove(str(file.file))
        return redirect(reverse('gestione:check_upload', args=[session.pk, files_not_supported]))

    return render(request, 'gestione/upload.html')


# ----------------------------------------------------------------------- #
#            view which shows the result of an upload session
# ----------------------------------------------------------------------- #
def check_upload(request, session, file_not_supported):
    ingestion_session = IngestionSession.objects.get(id=session)
    ingested_file = IngestedFile.objects.filter(ingestion_session=ingestion_session).filter(stato='ok')
    existing_file = IngestedFile.objects.filter(ingestion_session=session).filter(stato='already exists')

    context = {'ingested_file': ingested_file,
               'existing_file': existing_file,
               'files_not_supported': file_not_supported}
    return render(request, template_name='gestione/situazione_upload.html', context=context)


# ----------------------------------------------------------------------- #
# View for delete an ingested document object in a session, not an
# ingested document in PrivateGPT
# ----------------------------------------------------------------------- #
def cancel_file_object(request, file_pk, session_pk):
    ingested_file = IngestedFile.objects.get(pk=file_pk)
    file_path = str(ingested_file.file)
    os.remove(file_path)
    ingested_file.delete()
    return redirect('gestione:check_upload', session=session_pk, file_not_supported=[])


# -------------------------------------------------------------------------------------------- #
#
# -------------------------------------------------------------------------------------------- #
def edit_file_name(request, file_pk):

    file = IngestedFile.objects.get(pk=file_pk)
    ok_pattern = False
    while not ok_pattern:
        file_name, file_extension = os.path.splitext(file.file_name)

        version_pattern = re.compile(r'v_\d+$')

        if version_pattern.search(file_name):
            current_version = file_name.split('_')[-1]
            current_version = int(current_version)
            new_version = current_version + 1
            new_file_name = f'{file_name[:-len(str(current_version))] + str(new_version)}{file_extension}'
        else:
            new_file_name = f'{file_name}_v_1{file_extension}'

        file.file_name = new_file_name
        file.save()
        if not already_exist(new_file_name):
            file_path = str(file.file)
            dir_name = os.path.dirname(str(file.file))
            new_file_name = str(dir_name)+"/"+str(file.file_name)
            os.rename(file_path, new_file_name)
            file.file = new_file_name
            ingest_file(str(file.file))
            file.stato = 'ok'
            file.save()
            os.remove(str(file.file))

            file_not_supported = []
            return redirect(reverse('gestione:check_upload', args=[file.ingestion_session.pk, file_not_supported]))


# ------------------------------------------------------------------------------ #
# View for replace a document during the ingestion, this function delete the
# old version of document and ingest the actual version
# ------------------------------------------------------------------------------ #
def replace_file(request, file_pk):
    ingested_file = IngestedFile.objects.get(pk=file_pk)
    file_name = ingested_file.file_name

    delete_document(file_name)
    if ingest_file(str(ingested_file.file)):
        ingested_file.stato = 'ok'
        ingested_file.save()
        os.remove(str(ingested_file.file))
        file_not_supported = []
        return redirect(reverse('gestione:check_upload', args=[ingested_file.ingestion_session.pk, file_not_supported]))
    else:
        print("error during the new ingestion")


def create_question(request, answer_pk, satisfied):
    answer = Answer.objects.get(pk=answer_pk)
    satisfied = satisfied
    context = {'answer': answer, 'satisfied': satisfied}

    already_reported = Question.objects.filter(answer=answer).exists()
    if already_reported:
        return render(request, template_name="gestione/thx.html", context={'ok': 0})

    if request.method == 'POST':
        form = InsertQuestionForm(request.POST)

        # Se il form è valido creo e inserisco nel db la domanda
        if form.is_valid():
            question = Question()
            question.answer = answer
            question.satisfied = satisfied
            question.state = 0
            question.displayed = False
            question.comment = form.cleaned_data['comment']
            question.save()
            return render(request, template_name='gestione/thx.html', context={'ok': 1})
    else:
        form = InsertQuestionForm()
        context['form'] = form
        return render(request, template_name='gestione/crea_domanda.html', context=context)


# ----------------------------------------------------------------------------------------#
# View per mostrare tutte le domande in attesa di approvazione
# ----------------------------------------------------------------------------------------#
class QuestionList(PermissionRequiredMixin, ListView):
    permission_required = "is_staff"
    template_name = "gestione/question_list.html"
    model = Question

    # Queryset per decidere cosa visualizzare nel template
    def get_queryset(self):
        what_to_view = self.kwargs.get('what')

        # Domande ancora non visualizzate
        if what_to_view == 'not_displayed':
            queryset = Question.objects.filter(displayed=0).order_by('-answer__date')
        # Domande gia visualizzate e ancora non approvate  
        elif what_to_view == 'displayed_to_be_approved':
            queryset = Question.objects.filter(displayed=1).filter(state=0).order_by('-answer__date')
        # Domande gia approvate
        elif what_to_view == 'approved':
            queryset = Question.objects.filter(state=1).order_by('-answer__date')
        # Domande non approvate
        else:
            queryset = Question.objects.filter(state=2).order_by('-answer__date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['what'] = self.kwargs.get('what')
        context['questions'] = self.get_queryset()
        return context


def show_question(request, question_pk, state=0):
    question = Question.objects.get(pk=question_pk)
    context = {
        'question': question,
        'answers': Answer.objects.get(pk=question.answer.pk),
    }
    if request.method == 'GET':
        print("sono nella get")
        if not question.displayed:
            question.displayed = True
            question.save()
            context['displayed'] = '1'
        return render(request, template_name='gestione/mostra_domanda.html', context=context)
    else:
        # Se lo stato è uguale a 1 creo un nuovo documento con la coppia domanda_risposta e lo ingesto
        if state == 1:
            pass
        else:
            # La domanda passa in stato non approvato
            question.state = 2
            question.save()
            # Rendero su un template dove visualizzo un messaggio di ok e ritorno alla lista di domande
            return render(request, template_name="gestione/end_revisione.html")
