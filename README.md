"On the server, only install the required libraries and Celery, and add a user to RabbitMQ after that run genetic_algoritmV1.py.

On workstations:

Create a virtual environment.
Install libraries.
Copy the whole project to a folder.
Run this command: celery -A celery_app worker --loglevel=info.
This will allow the worker to begin negotiating with the server to start processing jobs in parallel."


note : all run scripts must be in screen in linux
