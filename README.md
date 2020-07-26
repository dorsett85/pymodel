# Quickmodel

A Django web application to upload datasets, visualize variables, and run statistical models.

[QuickModel](https://quickmodel.cphillipsdorsett.com/)

## setup

Required software
1. python 3.6 (newer versions may have issues installing requirements.txt)
2. mysql (with root password user and a 'pythonmodels' database)

### production setup (ssh'd into server as sudo root user 'clayton')

Required software (in addition to those required below the initial setup)
1. python3.6-dev
2. python3.6-venv
3. nginx

```shell
cd /var/www/
sudo git clone git@github.com:dorsett85/pymodel
sudo chown -R clayton:clayton pymodel/
cd pymodel/

# Make a virtual environment and install packages
python3.6 -m venv pyenv
source pyenv/bin/activate
pip install -r requirements.txt
pip install gunicorn

// Run the django migrations and static file collector 
python manage.py migrate
python manage.py collectstatic
```

Next up we'll follow the tutorial at this link (starting form "Testing Gunicorn’s Ability to Serve the Project"):

https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04
