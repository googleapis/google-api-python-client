#/bin/bash
#
# Run all the tests.
#
# The python interpreter to use is passed in on the command line.

FLAGS=--positional_parameters_enforcement=EXCEPTION
$1 runtests.py $FLAGS tests/test_discovery.py
$1 runtests.py $FLAGS tests/test_errors.py
$1 runtests.py $FLAGS tests/test_http.py
$1 runtests.py $FLAGS tests/test_json_model.py
$1 runtests.py $FLAGS tests/test_mocks.py
$1 runtests.py $FLAGS tests/test_model.py
$1 runtests.py $FLAGS tests/test_oauth2client_clientsecrets.py
$1 runtests.py $FLAGS tests/test_oauth2client_django_orm.py
$1 runtests.py $FLAGS tests/test_oauth2client_file.py
$1 runtests.py $FLAGS tests/test_oauth2client_jwt.py
$1 runtests.py $FLAGS tests/test_oauth2client.py
$1 runtests.py $FLAGS tests/test_protobuf_model.py
$1 runtests.py $FLAGS tests/test_schema.py
$1 runtests.py $FLAGS tests/test_oauth2client_appengine.py
$1 runtests.py $FLAGS tests/test_oauth2client_keyring.py
