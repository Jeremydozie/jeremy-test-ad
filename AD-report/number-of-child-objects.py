from googleapiclient.discovery import build
from google.oauth2 import service_account
from collections import defaultdict

# Replace with your service account file and source folder ID
SERVICE_ACCOUNT_FILE = 'service-account.json'
SOURCE_FOLDER_ID = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'

# Authenticate and build the service
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.readonly'])
service = build('drive', 'v3', credentials=creds)

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    return items

def count_child_objects(service, folder_id):
    total_files = 0
    total_folders = 0
    stack = [folder_id]

    while stack:
        current_folder = stack.pop()
        items = list_files_in_folder(service, current_folder)
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                total_folders += 1
                stack.append(item['id'])
            else:
                total_files += 1

    return total_files, total_folders

def generate_report(service, source_folder_id):
    report = defaultdict(lambda: {'files': 0, 'folders': 0})

    top_level_folders = list_files_in_folder(service, source_folder_id)
    for folder in top_level_folders:
        if folder['mimeType'] == 'application/vnd.google-apps.folder':
            folder_id = folder['id']
            files, folders = count_child_objects(service, folder_id)
            report[folder['name']]['files'] = files
            report[folder['name']]['folders'] = folders

    # Total nested folders in the source folder
    _, total_nested_folders = count_child_objects(service, source_folder_id)
    return report, total_nested_folders

def save_report_to_file(report, total_nested_folders, filename):
    with open(filename, 'w') as f:
        f.write("Report for each top-level folder:\n")
        for folder_name, counts in report.items():
            f.write(f"Folder: {folder_name}, Files: {counts['files']}, Folders: {counts['folders']}\n")
        f.write(f"\nTotal nested folders in the source folder: {total_nested_folders}\n")

def main():
    report, total_nested_folders = generate_report(service, SOURCE_FOLDER_ID)
    save_report_to_file(report, total_nested_folders, 'report-for-number-of-child-objects.txt')

    print('Report saved to report-for-number-of-child-objects.txt')

if __name__ == '__main__':
    main()