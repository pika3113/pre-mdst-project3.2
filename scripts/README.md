# Scripts Directory

This directory contains all utility scripts organized by category.

## Directory Structure

### `/setup/`
Scripts for initial project setup and configuration:
- `setup_auth.bat` - Set up authentication system
- `check_setup.bat` - Verify project setup

### `/debug/` 
Debug and testing utilities:
- `check_db.py` - Database debugging tools
- `debug_auth.py` - Authentication debugging
- `debug_balance.py` - Balance system debugging  
- `test_auth_system.py` - Authentication system tests

### `/docker/`
Docker-related scripts:
- `start_docker.bat` - Start Docker containers
- `stop_docker.bat` - Stop Docker containers

### Root Scripts
Main application launchers:
- `start_wordle_game.bat` - Start Wordle game only
- `start_wordle_with_auth.bat` - Start Wordle with authentication
- `start_complete_system.bat` - Start full system (in root directory, currently in use)

## Usage

Run scripts from the project root directory using relative paths:
```bash
# Setup
scripts/setup/setup_auth.bat
scripts/setup/check_setup.bat

# Docker management
scripts/docker/start_docker.bat
scripts/docker/stop_docker.bat

# Debug tools
python scripts/debug/check_db.py
python scripts/debug/debug_auth.py

# Game launchers
scripts/start_wordle_game.bat
scripts/start_wordle_with_auth.bat
```
