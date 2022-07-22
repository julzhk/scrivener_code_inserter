from unittest import TestCase

from main import GithubUrl


class test_parse_github_url(TestCase):

    def test_parse(self):
        g = GithubUrl(github_filepath='https://github.com/julzhk/policy_explorer/blob/master/persona/models.py#L8-L15')
        self.assertEqual(g.from_line, 8)
        self.assertEqual(g.to_line, 15)
        self.assertEqual(g.repo, 'policy_explorer')
        self.assertEqual(g.user, 'julzhk')
        self.assertEqual(g.filepath, 'persona/models.py')
