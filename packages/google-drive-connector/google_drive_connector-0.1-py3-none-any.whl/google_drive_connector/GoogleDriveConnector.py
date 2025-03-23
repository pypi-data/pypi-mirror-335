import yaml
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

class GoogleDriveConnector:
    def __init__(self, config_path="config.yaml"):
        self.config = self.load_config(config_path)
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.service_account_file = self.config["google_drive"]["service_account_file"]
        self.parent_folder_id = self.config["google_drive"]["parent_folder_id"]
        self.creds = self.authenticate()
        self.service = build('drive', 'v3', credentials=self.creds)

    @staticmethod
    def load_config(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def authenticate(self):
        return service_account.Credentials.from_service_account_file(self.service_account_file, scopes=self.scopes)

    def list_files(self):
        results = self.service.files().list(q=f"'{self.parent_folder_id}' in parents", fields="files(id, name)").execute()
        files = results.get("files", [])
        for idx, file in enumerate(files, start=1):
            print(f"{idx}. {file['name']}")
        return files

    def list_directories(self):
        results = self.service.files().list(q=f"'{self.parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'", fields="files(id, name)").execute()
        directories = results.get("files", [])
        for idx, directory in enumerate(directories, start=1):
            print(f"{idx}. {directory['name']}")
        return directories

    def upload_file(self, file_path):
        file_metadata = {'name': file_path.split('/')[-1], 'parents': [self.parent_folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print(f"File uploaded successfully! File ID: {file.get('id')}")