# rideMe

Ride sharing app for CSCI485 project

Can be viewed at https://rideme-app.herokuapp.com/ 

## Running instructions

Ensure that you have a code editor, Python 3.11.2 and PostgreSQL installed on 
your machine

Clone this repository and open in your code editor

The next step is to install and activate the Python virtual environment, which
can be done by entering 3 scripts into the terminal of your code editor in the 
project's root directory (i.e. same level as manage.py)

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
command
```
python manage.py migrate
```

Now, you should be ready to run the project! Run the following command, which will 
provide a link in the terminal to the locally running site
```
python manage.py runserver
```

## Testing Functionality

Note that it will take 3 days to test all of RideMe's functionality. Say you are testing
on April 5. The earliest trip date you can select to add a posting is April 6. After adding
a posting with a trip date of April 6, you then must create other accounts to send messages 
to the post owner, then log back in as the post owner to approve the users who messaged the 
post owner as passengers. Then, on April 6, the posting will disappear from the open postings 
query (unless all the available seats have been filled, in which case the posting will have 
already been removed). On April 7, the day after the trip date, the post owner will have the 
ability to complete the posting and review everyone who messaged them regarding the posting 
and all those who messaged the post owner regarding the posting will have the ability to 
review the post owner.
