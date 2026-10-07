import gunicorn


# Use a generic server token and do not disclose Gunicorn or Python.
gunicorn.SERVER = "web"
gunicorn.SERVER_SOFTWARE = "web"
