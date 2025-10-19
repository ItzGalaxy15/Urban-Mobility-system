"""
Central configuration file for Urban Mobility System.
Defines all file paths and system-wide constants.
"""
import os

# Get the absolute path to the src folder
SRC_FOLDER = os.path.abspath(os.path.dirname(__file__))

# Project root (parent of src)
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_FOLDER, '..'))

# Database file path
DB_FILE = os.path.join(SRC_FOLDER, 'urban_mobility.db')

# Log file path
LOG_FILE = os.path.join(SRC_FOLDER, 'activity.log')

# Backup directory
BACKUP_DIR = os.path.join(SRC_FOLDER, 'backups')
