import unittest
import doctest


class OptionalExtensionTestSuite(unittest.TestSuite):
    def run(self, result):
        import simplejson
        run = unittest.TestSuite.run
        run(self, result)
        simplejson._toggle_speedups(False)
        run(self, result)
        simplejson._toggle_speedups(True)
        return result


def additional_tests(suite=None):
    import simplejson
    import simplejson.encoder
    import simplejson.decoder
    if suite is None:
        suite = unittest.TestSuite()
    for mod in (simplejson, simplejson.encoder, simplejson.decoder):
        suite.addTest(doctest.DocTestSuite(mod))
    suite.addTest(doctest.DocFileSuite('../../index.rst'))
    return suite


def all_tests_suite():
    suite = unittest.TestLoader().loadTestsFromNames([
        'simplejson.tests.test_check_circular',
        'simplejson.tests.test_decode',
        'simplejson.tests.test_default',
        'simplejson.tests.test_dump',
        'simplejson.tests.test_encode_basestring_ascii',
        'simplejson.tests.test_encode_for_html',
        'simplejson.tests.test_fail',
        'simplejson.tests.test_float',
        'simplejson.tests.test_indent',
        'simplejson.tests.test_pass1',
        'simplejson.tests.test_pass2',
        'simplejson.tests.test_pass3',
        'simplejson.tests.test_recursion',
        'simplejson.tests.test_scanstring',
        'simplejson.tests.test_separators',
        'simplejson.tests.test_speedups',
        'simplejson.tests.test_unicode',
        'simplejson.tests.test_decimal',
    ])
    suite = additional_tests(suite)
    return OptionalExtensionTestSuite([suite])


def main():
    runner = unittest.TextTestRunner()
    suite = all_tests_suite()
    runner.run(suite)


if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    main()
