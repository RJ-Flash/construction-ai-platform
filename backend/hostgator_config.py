"""
HostGator Configuration for the Construction AI Platform

This module contains specific settings and configurations for deploying the
application on HostGator shared hosting. HostGator uses cPanel, which supports
running Python applications through Passenger WSGI.

INSTRUCTIONS:
1. Upload the entire application to your HostGator account via FTP or cPanel file manager
2. Rename this file to passenger_wsgi.py in the root directory of your hosting
3. Add a .htaccess file with the appropriate rewrite rules
4. Set up a Python environment in cPanel if not already available
5. Install the requirements using pip: pip install -r requirements.txt

For more information, see HostGator's documentation on Python application deployment.
"""

import sys
import os

# Add the application directory to the Python path
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Set up paths
cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/backend')

# Import the FastAPI application
from app.main import app

# Create a WSGI application
application = app
