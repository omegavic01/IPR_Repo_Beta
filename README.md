Welcome to the documentation for the backend of IPR Beta!
=========================================================

High level documentation specific to the scripts built for the IPR
project.  This repo is an attempt at updating the IPR_Repo scripts
from a imperative programming methodology to a more OOP style.

This is a prototype in development.

Was able to get it working within a virtual environment.  Python 
experience required.

Cheat Sheet:

Go to your virtual environment directory within a Git Bash terminal and run:
git clone https://github.com/omegavic01/IPR_Repo_Beta.git

Once repo is cloned change directory into IPR_Repo_Beta:
cd IPR_Repo_Beta/

*You will notice that you are in a git local repo under the master branch.

Create a python virtual environment (utilizing virtualenv):
virtualenv ipr_v2_venv

Activate virtual environment in preparation for installing packages:
source ipr_v2_venv/Scripts/activate

*You should now see the (ipr_v2_venv) tag within your git bash terminal.

Install packages within the requirements.txt file.  You should not have changed directories at this point.  Will need to be in the directory with the requirements.txt file.
pip install -r requirements.txt

Create an .env file from the .env_template with in the same directory.  Update the fields required fields.  This worked in pycharm however it did not work in windows file explorer.
DDI_USERNAME=<username>
DDI_PASSWORD=<password>
DDI_URL=<url>

Change diretory to IPR_Repo_Beta\src\data.

Run main.py:
python main.py

