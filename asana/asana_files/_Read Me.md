# Asana File Download Process Documentation

# _Suggestions for downloading large files - update script to place files on OneDrive not Documents_

## Overview
This document outlines the process for setting up and using the Asana file download script, which allows you to batch download files from your Asana workspace. Skip to step 2

## Prerequisites
- Python 3.9 or higher
- Access to Asana with administrative privileges
- Terminal/Command Line access

## Step 1: Initial Setup

### 1.1 Install Python Dependencies
Open Terminal and run the following command:
```bash
python3 -m pip install requests python-dotenv
```

### 1.2 Create Project Directory
1. Create a new directory for the project:
```bash
mkdir asana
cd asana
```

### 1.3 Generate Asana API Token
1. Go to https://app.asana.com/0/my-apps
2. Click "Create New Token"
3. Name: "File Downloads"
4. Copy the generated token immediately
5. Store it securely (you won't be able to see it again)

### 1.4 Create Configuration Files
1. Create `.env` file:
```bash
echo "ASANA_TOKEN=your_token_here" > .env
```
Replace `your_token_here` with your actual token

2. Save the Python script as `asana_downloader.py`

## Step 2: Running the Script

### 2.1 Basic Usage
1. Open Terminal
2. Navigate to your project directory:
```bash
cd path/to/asana
```
3. Run the script:
```bash
python3 asana_downloader.py
```

### 2.2 Script Behavior
- Creates an `asana_files` directory in the current location
- Organizes files by:
  - Date
  - Project name
  - Task name
- Downloads files from the past 30 days by default

### 2.3 Monitoring Progress
The script will show:
- Number of projects found
- Tasks with attachments
- Download progress for each file
- Final statistics

### 2.4 Stopping the Script
- Press `Control + C` to stop the script at any time
- On Mac, both `Command + C` and `Control + C` work
- Alternative: `Control + Z` as backup option

## Step 3: Troubleshooting

### 3.1 Common Issues and Solutions

#### Token Issues
- Error: "No token found in configuration files"
  - Solution: Check that `.env` file exists and contains the correct token
  - Verify no extra spaces in `.env` file

#### Permission Issues
- Error: "Permission denied"
  - Solution: Check write permissions in the directory
  - Run: `chmod 755 asana_downloader.py`

#### Download Issues
- Error: "Error downloading attachment"
  - Solution: Check internet connection
  - Verify token has proper permissions
  - Try running script again for failed downloads

### 3.2 File Location
- Default: `./asana_files/[DATE]/[PROJECT]/[TASK]/[FILE]`
- Example: `./asana_files/2024-10-30/Marketing Project/Design Task/file.pdf`

## Step 4: Maintenance

### 4.1 Regular Updates
- Keep Python packages updated:
```bash
python3 -m pip install --upgrade requests python-dotenv
```

### 4.2 Token Management
- Rotate API token every 90 days
- Delete unused tokens from Asana
- Never share tokens in code or documentation

### 4.3 Best Practices
- Run during off-peak hours for large downloads
- Monitor disk space before large downloads
- Keep backup of important configuration files
- Test script with small projects first

## Support Resources
- Asana API Documentation: https://developers.asana.com/docs
- Python Requests Library: https://docs.python-requests.org/
- For internal support: Contact IT Help Desk

## Change Log
- Initial Version: October 30, 2024
  - Basic download functionality
  - File organization by date/project/task
  - Progress monitoring
  - Error handling

