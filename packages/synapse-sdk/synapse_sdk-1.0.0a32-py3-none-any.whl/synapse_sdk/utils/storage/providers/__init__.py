from urllib.parse import parse_qs, urlparse


class BaseStorage:
    url = None
    options = None
    OPTION_CASTS = {}

    def __init__(self, connection_params: str | dict):
        self.url = None

        if isinstance(connection_params, dict):
            self.query_params = connection_params['configuration']
        else:
            self.url = urlparse(connection_params)
            self.query_params = self.url_querystring_to_dict()

    def url_querystring_to_dict(self):
        query_string = self.url.query

        query_dict = parse_qs(query_string)

        for key, value in query_dict.items():
            if len(value) == 1:
                query_dict[key] = value[0]

        return {
            key: self.OPTION_CASTS[key](value) if key in self.OPTION_CASTS else value
            for key, value in query_dict.items()
        }

    def upload(self, source, target):
        raise NotImplementedError

    def exists(self, target):
        raise NotImplementedError

    def get_url(self, target):
        raise NotImplementedError

    def get_pathlib(self, path):
        raise NotImplementedError
