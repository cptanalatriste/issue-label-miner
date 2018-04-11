"""
This module obtain issue and labelling information from GitHub
"""
import requests

import json
import pandas as pd
import bson.json_util as json_util

from pandas.io.json import json_normalize

SEARCH_REPOSITORIES_URL = "https://api.github.com/search/repositories"
LABELS_CSV_FILE =  "label_dataframe.csv"

# TODO(cgavidia): Only for testing
# PAGE_SIZE = 100
PAGE_SIZE = 30


def get_next_page(response):
    link_headers = response.headers.get('link', None).split(',')

    for link in link_headers:
        if 'rel="next"' in link:
            return link.split(";")[0][1: -1]

    return None


def get_labels(repositories):
    labels = []
    for repository in repositories:
        request_url = repository["labels_url"].replace('{/name}', '')
        print "get_labels->request_url: " + str(request_url)

        try:
            response = requests.get(request_url)
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

    while request_url is not None:
        print "search_repositories->request_url: " + str(request_url)
        try:
            response = requests.get(request_url, params=search_parameters)
            json_response = response.json()

            repositories.extend(json_response['items'])
            labels.extend(get_labels(json_response['items']))

            search_parameters = {}
            request_url = get_next_page(response)
        except Exception as e:
            print e
            break

        # TODO(cgavidia): Only for testing
        break

    return repositories, labels


def to_dataframe(json_response):
    json_sanitized = json.loads(json_util.dumps(json_response))
    json_normalized = json_normalize(json_sanitized)

    return pd.DataFrame(json_normalized)


def main():
    query = "created:>2018-01-01"

    repositories, labels = search_repositories(query)

    repo_dataframe = to_dataframe(repositories)
    label_dataframe = to_dataframe(labels)

    print repo_dataframe.columns
    print label_dataframe.columns

    repo_dataframe.to_csv("repo_dataframe.csv", encoding='utf-8')
    label_dataframe.to_csv(LABELS_CSV_FILE, encoding='utf-8')


if __name__ == "__main__":
    main()
