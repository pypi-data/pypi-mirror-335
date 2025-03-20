from upath import UPath

from synapse_sdk.utils.storage.providers import BaseStorage


class SFTPStorage(BaseStorage):
    def get_pathlib(self, path):
        credentials = self.query_params['params']
        host = self.query_params['host']
        root_path = self.query_params['root_path']

        username = credentials['username']
        password = credentials['password']
        if path == '/':
            path = ''
        return UPath(f'sftp://{host}', username=username, password=password) / root_path / path
