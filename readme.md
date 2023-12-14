# *_Interface for ptrivateGPT_* #
##### version 0.2 

## Necessary libraries ##


- __django__

       pip install django
  Django is the web framework with which this interface for privateGPT is created


- __reuests__

      pip install requests
  Library for making request 


- __django-braces__
  
        pip install django-braces
  Braces is alibrary to manage user's permissions


- __crispy_forms__ & __bootstrap__

        pip install django-crispy-forms
        pip install crispy_bootstrap4
  Libraries for making more beautifully forms and pages


## Starting the application ##
After installing all the necessary libraries, start the web server        

        python manage.py runserver
  
## Division of the application ##

- ## __interface_v2__ 
  In this module there is the code for user management



- ## __gestione__ ##

  In this module there are :
  
  - The URL of the privateGPT server 
  - A method to check the health of the server
  - A method for inserting new documents
    - A method for extracting content from documents
  - A method for viewing inserted documents
  - A method for deleting an inserted document
  - Some methods to interact with the chat and change the type of interaction
  - Some methods to manage user reports regarding correct/incorrect answers

      

