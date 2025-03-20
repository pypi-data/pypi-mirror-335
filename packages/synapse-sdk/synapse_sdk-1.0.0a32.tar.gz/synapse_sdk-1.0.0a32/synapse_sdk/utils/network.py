from urllib.parse import urlparse, urlunparse


def clean_url(url, remove_query_params=True, remove_fragment=True):
    parsed = urlparse(url)
    query = '' if remove_query_params else parsed.query
    fragment = '' if remove_fragment else parsed.fragment

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query,
        fragment,
    ))
