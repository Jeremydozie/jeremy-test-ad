from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'service-account.json'

# Scopes required for the script
SCOPES = ['https://www.googleapis.com/auth/drive']

# Authenticate and build the Google Drive service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

# Source and destination folder IDs
SOURCE_FOLDER_ID = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'
DESTINATION_FOLDER_ID = '1bpanj5cjqxv4TFAvSoLrF9RG_Ie5hMzI'

def copy_file(file_id, dest_folder_id):
    file = service.files().get(fileId=file_id).execute()
    copied_file = {
        'name': file['name'],
        'parents': [dest_folder_id]
    }
    return service.files().copy(fileId=file_id, body=copied_file).execute()

def copy_folder(source_folder_id, dest_folder_id):
    # List all files in the source folder
    query = f"'{source_folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            # Create a new folder in the destination
            new_folder = {
                'name': item['name'],
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [dest_folder_id]
            }
            created_folder = service.files().create(body=new_folder, fields='id').execute()
            # Recursively copy the contents of the folder
            copy_folder(item['id'], created_folder['id'])
        else:
            # Copy the file to the destination folder
            copy_file(item['id'], dest_folder_id)

# Copy content from source to destination
copy_folder(SOURCE_FOLDER_ID, DESTINATION_FOLDER_ID)

print("Content copied successfully.")
