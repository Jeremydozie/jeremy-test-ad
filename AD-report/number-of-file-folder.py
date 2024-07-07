import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set the source folder ID
SOURCE_FOLDER_ID = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'

# Define the scopes and the credentials file
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = 'service-account.json'

# Authenticate and construct the service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

def count_files_and_folders(service, folder_id):
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, mimeType)"
        ).execute()
        items = results.get('files', [])
        
        num_files = 0
        num_folders = 0
        
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                num_folders += 1
            else:
                num_files += 1
        
        return num_files, num_folders

    except HttpError as error:
        print(f'An error occurred: {error}')
        return 0, 0

def main():
    num_files, num_folders = count_files_and_folders(service, SOURCE_FOLDER_ID)
    report = f'Total number of files: {num_files}\nTotal number of folders: {num_folders}'
    
    # Save the report to a file
    with open('report-for-number-of-files-folders.txt', 'w') as report_file:
        report_file.write(report)
    
    print('Report saved to report-for-number-of-files-folders.txt')

if __name__ == '__main__':
    main()
