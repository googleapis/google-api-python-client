#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""One-line documentation for discovery module.

A detailed description of discovery.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import simplejson

def discovery():
  d = simplejson.load(open("discovery.json", "r"))
  desc = d["data"]["buzz"]["0.1"]
  base = desc["baseUrl"]
  feeds = desc["resources"]["feeds"]
  methods = feeds["methods"]
  list_method = methods["list"]
  print list_method

  class Proto(object):
    """A class for interacting with a service"""
    pass

  def doList(self, scope, userId):
    print "Hello"

  setattr(doList, "__doc__", "A description of how to use this function")
  setattr(Proto, "list", doList)

  return Proto()


def main():
  p = discovery()
  p.list("foo", "bar")
  print dir(p)
  print help(p)


if __name__ == '__main__':
  main()
