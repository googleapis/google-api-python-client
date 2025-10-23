# Logging

This page provides logging tips to help you debug your applications.

## Log Level

You can enable logging of key events in this library by configuring Python's standard [logging](http://docs.python.org/library/logging.html) module. You can set the logging level to one of the following:

- CRITICAL (least amount of logging)
- ERROR
- WARNING
- INFO
- DEBUG (most amount of logging)

In the following code, the logging level is set to `INFO`, and the Google Translate API is called:

```python
import logging
import sys
from googleapiclient.discovery import build

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Ensure logs are printed to stdout
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main():
    service = build('translate', 'v2', developerKey='your_api_key')
    result = service.translations().list(
        source='en',
        target='fr',
        q=['flower', 'car']
    ).execute()
    print(result)

if __name__ == '__main__':
    main()

```

The output of this code should print basic logging info:

```
INFO:root:URL being requested: https://www.googleapis.com/discovery/v1/apis/translate/v2/rest
INFO:root:URL being requested: https://www.googleapis.com/language/translate/v2?q=flower&q=car&source=en&alt=json&target=fr&key=your_api_key
{u'translations': [{u'translatedText': u'fleur'}, {u'translatedText': u'voiture'}]}
```

## HTTP Traffic

For even more detailed logging you can set the debug level of the [httplib2](https://github.com/httplib2/httplib2) module used by this library. The following code snippet enables logging of all HTTP request and response headers and bodies:

```python
import httplib2
httplib2.debuglevel = 4
```
