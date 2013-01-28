Setup Guide - Ubuntu Server 12.04 LTS
=====================================

Guide for installing dependencies and configuring Apache2 on Ubuntu Server 12.04 LTS.

Why Ubuntu Server 12.04 LTS?

The short answer is because SciPy is available from the official repository. CentOS 6 does not provide a pre-built SciPy package, and it is a rather involved process to build SciPy from source. Also, Amazon EC2 has a micro instance for Ubuntu Server 12.04 LTS which qualifies for it's Free Tier program (i.e. free for a year).

============
Installation
============

#.  Install Ubuntu 12.04 LTS (http://www.ubuntu.com/download/server).

#.  Update system packages

    ``apt-get upgrade``

#.  Install Apache and mod-wsgi

    ``apt-get install apache2``

    ``apt-get install libapache2-mod-wsgi``

#.  Install NumPy, matplotlib, and SciPy

    ``apt-get install python-numpy``

    ``apt-get install python-matplotlib``

    ``apt-get install python-scipy``

#.  We need Mercurial and pip to get the latest py-fcm

    ``apt-get install mercurial``

    ``apt-get install python-pip``

#.  Install py-fcm from the Mercurial repository.

    **Note: Do not pip install fcm. You will get errors due to the missing logicle.h file.**

    ``pip install hg+https://code.google.com/p/py-fcm/#egg=fcm``

#.  Use pip to install Django to get version 1.4. *You'll get v1.3 using apt-get*

    ``pip install django``

#.  Install Django app dependencies

    ``pip install django-extensions``

    ``pip install django-tastypie``

#.  Install git to get ReFlow

    ``apt-get install git``

#.  Clone ReFlow (for now, just put this somewhere like your home directory, we'll move it later)

    ``git clone https://github.com/whitews/ReFlow.git``

-------------------------
Optional, but recommended
-------------------------

*   Install iPython (always nice to have)

    ``apt-get install ipython``

-----------------
Choose a Database
-----------------

*   Install sqlite3 (more convenient for development)

    ``apt-get install sqlite3``

*   Install PostgreSQL and postgresql_psycopg2 driver

    ``apt-get install postgresql``

    ``apt-get install python-psycopg2``

=============
Configuration
=============

There are essentially 4 separate configuration tasks:

* Create an Apache2 VirtualHost
* Create a mod_wsgi script
* Create the Django Settings File
* Create a PostgreSQL Database

--------------------------
Create Apache2 VirtualHost
--------------------------

#.  Copy the default VirtualHost

    ``sudo cp /etc/apache2/sites-available/default /etc/apache2/sites-available/reflow``

#.  The new VirtualHost file should look like this:

    ::

        <VirtualHost *:80>
            ServerAdmin webmaster@localhost

            WSGIScriptAlias / /srv/django-projects/ReFlow/reflow/wsgi.py
            WSGIApplicationGroup %{GLOBAL}

            <Directory /srv/django-projects/ReFlow/reflow>

                AllowOverride None

                <Files wsgi.py>
                    Order allow,deny
                    Allow from all
                </Files>

            </Directory>

            Alias /static /srv/django-projects/ReFlow-static/

            ErrorLog ${APACHE_LOG_DIR}/reflow-error.log

            # Possible values include: debug, info, notice, warn, error, crit,
            # alert, emerg.
            LogLevel warn

            CustomLog ${APACHE_LOG_DIR}/reflow-access.log combined
        </VirtualHost>

#.  Edit apache2.conf file

    Note: If you need any of these features for other Virtual Hosts, edit as necessary. This list is meant as a guide for turning off certain Apache features that are not used by the ReFlow project.

    *   Hide the Apache version number and OS details

        ``ServerSignature Off``
        ``ServerTokens Prod``

    *   Disable directory browsing

        ``Options -Indexes``

    *   Disable server side includes

        ``Options -Includes``

    *   Disable CGI

        ``Options -ExecCGI``


--------------------------
Create a mod_wsgi script
--------------------------

#.  From our VirtualHost WSGIScriptAlias, we'll need to create a wsgi.py script here:

    ``/srv/django-projects/ReFlow/reflow/wsgi.py``

#.  Edit the wsgi.py file to look like this:

    ::

        import os
        import sys

        # Set matplotlib configuration directory, else Django complains it is not writable
        # We'll just use a tempfile
        import tempfile
        os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

        paths = [
            '/srv/django-projects/ReFlow',
            '/srv/django-projects/ReFlow/reflow'
        ]

        for path in paths:
            if path not in sys.path:
                sys.path.append(path)

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reflow.settings")

        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()


-------------------------
Create Django settings.py
-------------------------

#.  Copy the settings_sample.py to settings.py

    ``sudo cp /srv/django-projects/ReFlow/reflow/settings_sample.py /srv/django-projects/ReFlow/reflow/settings.py``

#.  Edit the settings.py file

    *   Turn off debugging

        ``Debug = False``

    *   Change BASE_DIR

        ``BASE_DIR = '/srv/django-projects'``

    *   Change DATABASES to whichever database you are using. For example, PostgreSQL would look similar to:

        ::

            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': 'somedb',
                    'USER': 'someuser',
                    'PASSWORD': 'somepassword',
                    'HOST': 'somehost',
                    'PORT': '5432', # or whatever port your DB is listening on
                }
            }

    *   Change TIME_ZONE according to http://en.wikipedia.org/wiki/List_of_tz_zones_by_name

    *   Change MEDIA_ROOT to the locate where user uploaded files will be stores. This is where the FCS files will live.

    *   Change SECRET_KEY to a new super secret key. If you have already cloned the ReFlow project and have django_extensions installed, you can generate a new random key using:

        ``python manage.py generate_secret_key``

        Copy and paste the output as the new SECRET_KEY value.

--------------------------
Create PostgreSQL Database
--------------------------

#.  Become 'postgres' user

    ``sudo posgres``

#.  Open PostgreSQL Shell

    ``psql``

#.  Create Database and User

    ``CREATE DATABASE somedb;``

    ``CREATE USER someuser WITH PASSWORD 'somepassword';``

#.  Grant DB Access to the User

    ``GRANT ALL PRIVILEGES ON DATABASE somedb TO someuser;``

#.  Edit the PostgreSQL configuration file ``pg_hba.conf`` to all local access for the user to the new DB by adding the following line:

    ``local    somedb    someuser        password``

#.  Restart PostgreSQL

    ``service postgresql restart``

#.  From ``/srv/django-projects/ReFlow/`` run manage.py with syncdb option. Follow the prompts for create an Django admin user.

    ``python manage.py syncdb``


==============
Restart Apache
==============

That's it! If everything was configured correctly just restart apache:

``service apache2 restart``