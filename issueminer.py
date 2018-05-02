"""
This module obtain issue and labelling information from GitHub
"""
import requests

import json
import pandas as pd
import bson.json_util as json_util

from pandas.io.json import json_normalize

import minerconfig

SEARCH_REPOSITORIES_URL = "https://api.github.com/search/repositories"
LABELS_CSV_FILE = "label_dataframe.csv"
REPOSITORY_CSV_FILE = "repo_dataframe.csv"

PAGE_SIZE = 100
MAX_REPOSITORIES = 500


def get_next_page(response):
    link_headers = response.headers.get('link', None).split(',')

    for link in link_headers:
        if 'rel="next"' in link:
            return link.strip().split(";")[0][1: -1]

    return None


def get_labels(repositories):
    labels = []
    for repository in repositories:
        request_url = repository["labels_url"].replace('{/name}', '')
        print "get_labels->request_url: " + str(request_url)

        try:
            response = requests.get(request_url, headers=minerconfig.AUTH_HEADER)
            json_response = response.json()
            labels.extend(json_response)
        except Exception as e:
            print e
            break

    return labels


def search_repositories(query):
    repositories = []
    labels = []

    search_parameters = {'q': query,
                         'sort': 'forks',
                         'order': 'desc',
                         'per_page': PAGE_SIZE}

    request_url = SEARCH_REPOSITORIES_URL

    while request_url is not None and len(repositories) <= MAX_REPOSITORIES:
        print "search_repositories->request_url: " + str(request_url)
        try:
            response = requests.get(request_url, params=search_parameters, headers=minerconfig.AUTH_HEADER)
            json_response = response.json()

            repositories.extend(json_response['items'])
            labels.extend(get_labels(json_response['items']))

            search_parameters = {}
            request_url = get_next_page(response)
        except Exception as e:
            print e
            break

    return repositories, labels


def to_dataframe(json_response):
    json_sanitized = json.loads(json_util.dumps(json_response))
    json_normalized = json_normalize(json_sanitized)

    return pd.DataFrame(json_normalized)


def main():
    query = "created:>2017-01-01"

    repositories, labels = search_repositories(query)

    repo_dataframe = to_dataframe(repositories)
    label_dataframe = to_dataframe(labels)

    print "len(repo_dataframe.index): " + str(len(repo_dataframe.index))
    print "len(label_dataframe.index): " + str(len(label_dataframe.index))

    repo_dataframe.to_csv(REPOSITORY_CSV_FILE, encoding='utf-8')
    label_dataframe.to_csv(LABELS_CSV_FILE, encoding='utf-8')


if __name__ == "__main__":
    main()
