import re

import nltk
import pandas as pd
import webcolors

import issueminer

FIELD_NAME = ["Priority"]

JIRA_V63_PRIORITIES = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']

# From: https://confluence.atlassian.com/jira064/what-is-an-issue-720416138.html
JIRA_V64_PRIORITIES = ['Highest', 'High', 'Medium', 'Low', 'Lowest']

# From: https://www.mediawiki.org/wiki/Bugzilla/Fields#Priority
BUGZILLA_FIELDS = ["Priority", "Severity"]
BUGZILLA_PRIORITIES = ['immediate', 'highest', 'high', 'normal', 'low', 'lowest']

CONSOLIDATED_CSV_FILE = "repository_using_priorities.csv"

SAMPLE_CSV_FILE = "sample_repositories_with_labels.csv"
SAMPLE_SIZE = 30
SEED = 123


# From: https://stackoverflow.com/questions/9694165/convert-rgb-color-to-english-color-name-like-green-with-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    try:
        closest_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        print "Color name not found for", requested_colour, ". Closest found: ", closest_name

    return closest_name


def get_repository_url(label_url):
    index = label_url.find("/labels/")
    repository_url = label_url[:index]

    return repository_url


def is_using_priorities_from_text(label_collection):
    porter_stemmer = nltk.PorterStemmer()

    repository_labels = [re.findall(r"[\w']+", label) for label in label_collection]
    repository_tokens = [porter_stemmer.stem(token.lower()) for token_list in repository_labels for token in
                         token_list]

    unified_terms = [porter_stemmer.stem(priority_label.lower()) for priority_label in
                     JIRA_V63_PRIORITIES + JIRA_V64_PRIORITIES + BUGZILLA_PRIORITIES + FIELD_NAME]

    return bool(set(repository_tokens) & set(unified_terms))


def is_using_priorities_from_color(label_colors):
    contains_red = any(['red' in color.lower() for color in label_colors])
    contains_yellow = any(['yellow' in color.lower() for color in label_colors])
    contains_green = any(['green' in color.lower() for color in label_colors])

    return contains_red and contains_yellow and contains_green


def main():
    labels_daframe = pd.read_csv(issueminer.LABELS_CSV_FILE)
    labels_daframe['repository_url'] = labels_daframe.apply(lambda label_info: get_repository_url(label_info['url']),
                                                            axis=1)
    repo_daframe = pd.read_csv(issueminer.REPOSITORY_CSV_FILE)
    repo_daframe.sample(n=SAMPLE_SIZE, random_state=SEED).to_csv(SAMPLE_CSV_FILE)
    print "Manual validation file stored in " + SAMPLE_CSV_FILE

    repositories = labels_daframe['repository_url'].unique()

    results_list = []
    for repository_url in repositories:
        label_series = labels_daframe[labels_daframe['repository_url'] == repository_url]

        repository_labels = [label.split() for label in label_series['name']]
        repository_tokens = [token.lower() for token_list in repository_labels for token in token_list]

        label_colors = [get_colour_name(webcolors.hex_to_rgb("#" + str(color))) for color in label_series['color']]

        using_priorities_text = is_using_priorities_from_text(label_series['name'])
        using_priorities_color = is_using_priorities_from_color(label_colors)

        results_list.append({'repository_url': repository_url,
                             'labels': ';'.join(repository_tokens),
                             'using_priorities_text': using_priorities_text,
                             'label_colors': ';'.join(label_colors),
                             'using_priorities_color': using_priorities_color,
                             'using_priorities': using_priorities_text or using_priorities_color})

    result_dataframe = pd.DataFrame(results_list)

    using_priorities = result_dataframe[result_dataframe['using_priorities'] == True]
    not_using_priorities = result_dataframe[result_dataframe['using_priorities'] == False]

    print "len(repositories.index): " + str(len(repositories))

    print "len(using_priorities.index): " + str(len(using_priorities.index)) + " " + str(
        float(len(using_priorities.index)) / len(repositories))

    print "len(not_using_priorities.index): " + str(len(not_using_priorities.index)) + " " + str(
        float(len(not_using_priorities.index)) / len(repositories))

    result_dataframe.to_csv(CONSOLIDATED_CSV_FILE)
    print "Results written in " + CONSOLIDATED_CSV_FILE


if __name__ == "__main__":
    main()
