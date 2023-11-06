from abc import ABC, abstractmethod
import pysftp
import os
from google.cloud import storage
import google.oauth2


class IO(ABC):

    @abstractmethod
    def download_folder(self, remote_folder, local_folder):
        pass

    @abstractmethod
    def download_file(self, remote_file, local_file):
        pass

    @abstractmethod
    def upload_folder(self, local_folder, remote_folder):
        pass
    
    @abstractmethod
    def upload_file(self, local_file, remote_file):
        pass

    @abstractmethod
    def listdir(self, remote_directory) -> list:
        pass

    @abstractmethod
    def isfile(self, remote_file) -> bool:
        pass

    @abstractmethod
    def isdir(self, remote_folder) -> bool:
        pass

class OnpremIO(IO):
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None  # Disable host key checking
    
    def join(self, *paths) -> str:
        return self._sep.join(paths).replace("/", self._sep).replace("\\", self._sep)

    def connect(self):
        self.sftp = pysftp.Connection(self.host, port=self.port, username=self.username, password=self.password, cnopts=self.cnopts)
        if self.sftp.remote_server_type == 'posix':
            self._sep = '/'
        elif self.sftp.remote_server_type == 'nt':
            self._sep = '\\'
        else:
            self._sep = '/'

    def disconnect(self):
        if self.sftp is not None:
            self.sftp.close()
    
    @property
    def sep(self) -> str:
        return self._sep

    def __enter__(self):
        self.sftp = pysftp.Connection(self.host, username=self.username, password=self.password, cnopts=self.cnopts)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.sftp:
            self.sftp.close()

    # def download_folder(self, remote_folder, local_folder):
    #     remote_root, folder_name = os.path.split(remote_folder)
    #     self.sftp.chdir(remote_root)
    #     self.sftp.get_r(folder_name, local_folder)

    #     for attr, path in self.sftp.listdir_attr(remote_folder):
    #         if attr.st_mode is not None:
    #             print(f"Uzak dosya: {path}")
    #             self.sftp.g
    #         elif self.sftp.isdir(path):
    #             print(f"Uzak klasör: {path}")
    
    def download_folder(self, remote_folder, local_folder):
        # remote_root, folder_name = os.path.split(remote_folder)
        # self.sftp.chdir(remote_root)
        os.makedirs(local_folder, exist_ok=True)
        for name in self.sftp.listdir(remote_folder):
            if self.sftp.isdir(self.join(remote_folder, name)):
                self.download_folder(self.join(remote_folder, name, sep=self.sep), os.path.join(local_folder, name))
                # self.sftp.chdir(remote_root)
            else:
                self.sftp.get(self.join(remote_folder, name), os.path.join(local_folder, name))



    def download_file(self, remote_file, local_file):
        self.sftp.get(remote_file, local_file)

    # def upload_folder(self, local_folder, remote_folder):
    #     if not self.sftp.isdir(remote_folder):
    #         self.sftp.mkdir(remote_folder)
    #     self.sftp.put_r(local_folder, remote_folder)

    def upload_folder(self, local_folder, remote_folder):
        self.sftp.makedirs(remote_folder)
        for name in os.listdir(local_folder):
            if os.path.isdir(os.path.join(local_folder, name)):
                self.upload_folder(os.path.join(local_folder, name), self.join(remote_folder, name))
            else:
                self.sftp.put(os.path.join(local_folder, name), self.join(remote_folder, name))

    def upload_file(self, local_file, remote_file):
        self.sftp.put(local_file, remote_file)

    def listdir(self, remote_directory) -> list:
        return self.sftp.listdir(remote_directory)
    
    def isfile(self, remote_file) -> bool:
        return self.sftp.isfile(remote_file)
    
    def isdir(self, remote_folder) -> bool:
        return self.sftp.isdir(remote_folder)


class GoogleCloudIO(IO):

    def __init__(self, account_service: dict, bucket_name: str) -> None:
        self.account_service = account_service
        self.bucket_name = bucket_name

    def join(self, *paths) -> str:
        return '/'.join(paths).replace("\\", '/')
    
    def connect(self):
        self.storage_client = storage.Client.from_service_account_info(self.account_service)

    def disconnect(self):
        self.storage_client.close()
    
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()
    
    def download_folder(self, remote_folder, local_folder):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        if not remote_folder.endswith('/'): remote_folder += '/'
        blobs = bucket.list_blobs(prefix=remote_folder)

        for blob in blobs:
            if blob.name.endswith('/'):
                # Bu bir klasördür, özyinelemeli olarak alt klasörü indirin
                # self.download_folder(blob.name, local_folder)
                pass
            else:
                # Bu bir dosyadır, indirin ve belirtilen hedef dizine kaydedin
                destination_path = self.join(local_folder, blob.name)
                root_path, _ = os.path.split(destination_path)
                os.makedirs(root_path, exist_ok=True)
                blob.download_to_filename(destination_path)
                print(f"Downloaded {blob.name} to {destination_path}")


    
    def download_file(self, remote_file, local_file):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(remote_file)
        blob.download_to_filename(local_file)
        print(f"Downloaded {remote_file} to {local_file}")

    
    def upload_folder(self, local_folder, remote_folder):
        bucket = self.storage_client.get_bucket(self.bucket_name)

        for root, _, files in os.walk(local_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                remote_blob_name = self.join(remote_folder, os.path.relpath(local_file_path, local_folder))
                blob = bucket.blob(remote_blob_name)
                blob.upload_from_filename(local_file_path)
                print(f"Uploaded {local_file_path} to {self.join(self.bucket_name, remote_blob_name)}")
            
    
    
    def upload_file(self, local_file, remote_file):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(local_file)

        blob.upload_from_filename(local_file)
        print(f"Uploaded {local_file} to {self.bucket_name}/{remote_file}")

    
    def listdir(self, remote_directory:str) -> list:
        bucket = self.storage_client.get_bucket(self.bucket_name)
        if not remote_directory.endswith('/'):
            remote_directory += '/'
        # List objects in the bucket with the specified prefix
        blobs = bucket.list_blobs(prefix=remote_directory)
        return list({blob.name[len(remote_directory):].split("/")[0] for blob in blobs if blob.name != remote_directory})


    
    def isfile(self, remote_file) -> bool:
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(remote_file)
        return blob.exists()

    
    def isdir(self, remote_folder) -> bool:
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=remote_folder)
        # If any objects exist with the specified prefix, consider it as the directory exists
        return any(blob for blob in blobs)
    