#!/bin/bash

openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
  -keyout privatekey.pem -out publickey.pem \
  -subj "/CN=unit-tests"

openssl pkcs12 -export -out privatekey.p12 \
  -inkey privatekey.pem -in publickey.pem \
  -name "key" -passout pass:notasecret

openssl pkcs12 -in privatekey.p12 \
  -nodes -nocerts -passout pass:notasecret \
  -passin pass:notasecret > pem_from_pkcs12.pem