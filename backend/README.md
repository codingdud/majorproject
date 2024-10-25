# Help Commands  

  ---
pip list  
pipenv lock -r

# new venv in python

`python -m venv c:\path\to\myenv`

# how to use!

`C:\> <venv>\Scripts\activate.bat`
`venv\Scripts\activate`

# deactivate
just type `deactivate` in the terimnal

# save pakages
when you finish your project, just type
`pip freeze > requirements.txt`
and then send this file to whoever needs it

### Docker Build
`Dockerfile | docker build -`
`docker build -t my-flask-app .`

### Doker run 
`docker run -p 5000:5000 my-flask-app`

### Run 
` flask --app hello run --debug`