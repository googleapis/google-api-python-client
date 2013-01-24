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


class KeyConversionTests(unittest.TestCase):

  def test_key_conversions(self):
    d = {'somekey': 'some value', 'another': 'something else', 'onemore': 'foo'}
    tuple_key = util.dict_to_tuple_key(d)

    # the resulting key should be naturally sorted
    self.assertEqual(
        (('another', 'something else'),
         ('onemore', 'foo'),
         ('somekey', 'some value')),
        tuple_key)

    # check we get the original dictionary back
    self.assertEqual(d, dict(tuple_key))
