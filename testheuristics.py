import unittest
import labelanalysis


class TestHeuristics(unittest.TestCase):

    def test_jira_labels(self):
        response_for_jira = labelanalysis.is_using_priorities_from_text(labelanalysis.JIRA_V64_PRIORITIES)
        self.assertTrue(response_for_jira)

    def test_github_labels(self):
        # From: https://help.github.com/en/articles/about-labels
        github_labels = ["bug", "documentation", "duplicate", "enhancement", "good first issue", "help wanted",
                         "invalid", "question", "wontfix"]
        response_for_github = labelanalysis.is_using_priorities_from_text(github_labels)
        self.assertFalse(response_for_github)

    def test_with_extra_tokens(self):
        bugzilla_with_tokens = ["priority:" + priority_label for priority_label in labelanalysis.BUGZILLA_PRIORITIES]

        response_for_bugzilla = labelanalysis.is_using_priorities_from_text(bugzilla_with_tokens)
        self.assertTrue(response_for_bugzilla)

    def test_priority_levels(self):
        priority_levels = ["Priority:" + str(level) for level in range(1, 6)]
        response_for_levels = labelanalysis.is_using_priorities_from_text(priority_levels)

        self.assertTrue(response_for_levels)


if __name__ == "__main__":
    unittest.main()
