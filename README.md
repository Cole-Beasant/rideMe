# rideMe

Ride sharing app for CSCI485 project

Can be viewed at https://rideme-app.herokuapp.com/ 

## Running instructions

Ensure that you have a code editor, Python 3.11.2 and PostgreSQL installed on 
your machine

Clone this repository and open in your code editor

The next step is to install and activate the Python virtual environment, which
can be by entering 3 scripts into the terminal of your code editor in the project's
root directory (i.e. same level as manage.py)

FOR WINDOWS 
```
pip install virtualenv
virtualenv venv
venv\Scripts\activate
```

FOR MAC 
```
python3 -m pip install virtualenv
python3 -m venv venv
source venv/bin/activate
```
Next, you must install the dependencies using the following command

FOR WINDOWS
```
pip install -r requirements.txt
```

FOR MAC
```
pip3 install -r requirements.txt
```

Next, make a file in the root directory titled ".env", and paste the following into
the file
```
SECRET_KEY=django-insecure-6)eg-3mzykmw#73!xs!l!(+8w4zan-vw2(r6t+gsh!^et5_a#n
```

Now you must migrate the data models to the PostgreSQL database using the following
commaand
```
python manage.py migrate
```

Now, you should be ready to run the project! Run the following command, which will 
provide a link in the terminal to the locally running site
```
python manage.py runserver
```
