from unittest import TestCase
from cStringIO import StringIO

import simplejson as json

class TestDump(TestCase):
    def test_dump(self):
        sio = StringIO()
        json.dump({}, sio)
        self.assertEquals(sio.getvalue(), '{}')

    def test_dumps(self):
        self.assertEquals(json.dumps({}), '{}')

    def test_encode_truefalse(self):
        self.assertEquals(json.dumps(
                 {True: False, False: True}, sort_keys=True),
                 '{"false": true, "true": false}')
        self.assertEquals(json.dumps(
                {2: 3.0, 4.0: 5L, False: 1, 6L: True, "7": 0}, sort_keys=True),
                '{"false": 1, "2": 3.0, "4.0": 5, "6": true, "7": 0}')

    def test_ordered_dict(self):
        # http://bugs.python.org/issue6105
        items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]
        s = json.dumps(json.OrderedDict(items))
        self.assertEqual(s, '{"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}')