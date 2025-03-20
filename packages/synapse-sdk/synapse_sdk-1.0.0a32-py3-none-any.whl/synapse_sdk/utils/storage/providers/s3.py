from upath import UPath

from synapse_sdk.utils.storage.providers import BaseStorage


class S3Storage(BaseStorage):
    ENDPOINT_URL = 'https://s3.amazonaws.com'
    DEFAULT_REGION = 'us-east-1'

    def __init__(self, url):
        super().__init__(url)

        self.upath = self._get_upath()

    def _get_upath(self):
        upath_kwargs = {
            'key': self.query_params['access_key'],
            'secret': self.query_params['secret_key'],
            'client_kwargs': {'region_name': self.query_params.get('region_name')},
        }

        if self.query_params.get('endpoint_url'):
            upath_kwargs['endpoint_url'] = self.query_params['endpoint_url']

        return UPath(
            f's3://{self.query_params["bucket_name"]}',
            **upath_kwargs,
        )

    def upload(self, source, target):
        with open(source, 'rb') as file:
            self.upath.write_text(file.read(), target)

        return self.get_url(target)

    def exists(self, target):
        return self.upath.exists(target)

    def get_url(self, target):
        return str(self.upath.joinuri(target))

    def get_pathlib(self, path):
        return self.upath.joinuri(path)
