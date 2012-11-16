"""Unit tests for oauth2client.util."""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import unittest

from oauth2client import util


class ScopeToStringTests(unittest.TestCase):

  def test_iterables(self):
    cases = [
      ('', ''),
      ('', ()),
      ('', []),
      ('', ('', )),
      ('', ['', ]),
      ('a', ('a', )),
      ('b', ['b', ]),
      ('a b', ['a', 'b']),
      ('a b', ('a', 'b')),
      ('a b', 'a b'),
      ('a b', (s for s in ['a', 'b'])),
    ]
    for expected, case in cases:
      self.assertEqual(expected, util.scopes_to_string(case))
