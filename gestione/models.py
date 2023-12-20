from django.db import models
from django.contrib.auth.models import User


# ------------------------------------------------------------------------------------------------ #
#                     Class that describes the response model
# ------------------------------------------------------------------------------------------------ #
class Answer(models.Model):
    # text of the request made by the user
    user_request = models.CharField(max_length=2048)
    # text of response made by E-lista
    answer = models.CharField(max_length=8000)
    # date of request
    date = models.DateTimeField(auto_now_add=True)
    # user that make request
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # doc-id that caused the response
    doc_id = models.CharField(max_length=60, blank=True, null=True)
    # name of file that caused the response
    file_name = models.CharField(max_length=60, blank=True, null=True)


# ------------------------------------------------------------------------------------------------ #
#                     Class that describes the request model
# ------------------------------------------------------------------------------------------------ #
class Question(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    # ****************************************** #
    # state = 0 === Answer to be approved
    # state = 1 === Answer approved
    # state = 2 === Answer not approved
    state = models.IntegerField(default=0)
    # ****************************************** #
    # False = not displayed
    # True = displayed
    displayed = models.BooleanField(default=False)
    # is user satisfied of response ?
    satisfied = models.BooleanField(default=False)
    # comment from the user who sends the question to the admin
    comment = models.CharField(max_length=300, default=' ')


# ------------------------------------------------------------------------------------------------ #
#       Class that describes the request model for Embedded model
# ------------------------------------------------------------------------------------------------ #
class DocRetrivalRequest(models.Model):
    user_request = models.CharField(max_length=2048)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class DocRetrivalResponse(models.Model):
    doc_request = models.ForeignKey(DocRetrivalRequest, on_delete=models.CASCADE)
    text = models.CharField(max_length=2048)
    score = models.IntegerField(default=0)
    file_name = models.CharField(max_length=60, blank=True, null=True)
    doc_id = models.CharField(max_length=60, blank=True, null=True)
