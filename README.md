## Build Guide
### Install curl
sudo apt-get install curl
#### Install python3.8
sudo apt-get install python3.8
sudo apt-get install python3.8-distutils
### Install python3.8-pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.8 get-pip.py
python3.8 -m pip install --upgrade pip
### Install virtualenv
python3 -m pip install virtualenv
### Set up virtualenvironment for scrape engine
python3.8 -m venv /var/www/virtualenv
