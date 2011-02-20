import os
import pydoc
import re

from apiclient.discovery import build

BASE = 'docs/dyn'

APIS = [
      ('buzz', 'v1'),
      ('moderator', 'v1'),
      ('latitude', 'v1'),
      ('customsearch', 'v1'),
      ('diacritize', 'v1'),
      ('translate', 'v2'),
      ('prediction', 'v1.1'),
      ('shopping', 'v1'),
      ('urlshortener', 'v1'),
      ]

def document(resource, path):
  print path
  collections = []
  for name in dir(resource):
    if not "_" in name and callable(getattr(resource, name)) and hasattr(
          getattr(resource, name), '__is_resource__'):
      collections.append(name)

  obj, name = pydoc.resolve(type(resource))
  page = pydoc.html.page(
      pydoc.describe(obj), pydoc.html.document(obj, name))

  for name in collections:
    page = re.sub('strong>(%s)<' % name, r'strong><a href="%s">\1</a><' % (path + name + ".html"), page)
  for name in collections:
    document(getattr(resource, name)(), path + name + ".")

  f = open(os.path.join(BASE, path + 'html'), 'w')
  f.write(page)
  f.close()

def document_api(name, version):
  service = build(name, version)
  document(service, '%s.%s.' % (name, version))

if __name__ == '__main__':
  for name, version in APIS:
    document_api(name, version)

