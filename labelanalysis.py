import pandas as pd
import issueminer

JIRA_V63_PRIORITIES = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']

# From: https://confluence.atlassian.com/jira064/what-is-an-issue-720416138.html
JIRA_V64_PRIORITIES = ['Highest', 'High', 'Medium', 'Low', 'Lowest']

# From: https://www.mediawiki.org/wiki/Bugzilla/Fields#Priority
BUGZILLA_PRIORITIES = ['immediate', 'highest', 'high', 'normal', 'low', 'lowest']

def get_repository_url(label_url):
    index = label_url.find("/labels/")
    repository_url = label_url[:index]

    return repository_url


def is_using_priorities(label_names):
    unified_terms = [priority_label.lower() for priority_label in
                     JIRA_V63_PRIORITIES + JIRA_V64_PRIORITIES + BUGZILLA_PRIORITIES]

    return bool(set(label_names) & set(unified_terms))


def main():
    labels_daframe = pd.read_csv(issueminer.LABELS_CSV_FILE)
    labels_daframe['repository_url'] = labels_daframe.apply(lambda label_info: get_repository_url(label_info['url']),
                                                            axis=1)

    repositories = labels_daframe['repository_url'].unique()

    results_list = []
    for repository_url in repositories:
        label_series = labels_daframe[labels_daframe['repository_url'] == repository_url]

        repository_labels = [label.lower() for label in label_series['name']]
        using_priorities = is_using_priorities(repository_labels)

        results_list.append({'repository_url': repository_url,
                             'using_priorities': using_priorities,
                             'labels': ' '.join(repository_labels)})

    result_dataframe = pd.DataFrame(results_list)

    using_priorities = result_dataframe[result_dataframe['using_priorities'] == True]
    not_using_priorities = result_dataframe[result_dataframe['using_priorities'] == False]

    print "len(repositories.index): " + str(len(repositories))

    print "len(using_priorities.index): " + str(len(using_priorities.index)) + " " + str(
        float(len(using_priorities.index)) / len(repositories))

    print "len(not_using_priorities.index): " + str(len(not_using_priorities.index)) + " " + str(
        float(len(not_using_priorities.index)) / len(repositories))

    result_dataframe.to_csv("repository_using_priorities.csv")


if __name__ == "__main__":
    main()
