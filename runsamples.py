#!/usr/bin/env python
"""Execute all sample applications.

Runs over all the sample applications, determines their type (App Engine,
Django, or a command-line application), and then runs them checking for a good
return status in the case of command-line applications and a 200 OK response in
the case of the App Engine and Django samples.
"""
import gflags
import httplib2
import logging
import os
import signal
import subprocess
import sys
import time

FLAGS = gflags.FLAGS

gflags.DEFINE_list('samples_to_skip', ['latitude'],
    'A comma separated list of project directory names to be skipped.')

gflags.DEFINE_enum('logging_level', 'INFO',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

gflags.DEFINE_string('app_engine_dir', '../google_appengine/',
    'Directory where Google App Engine is installed.')

gflags.DEFINE_string('sample_root', 'samples/oauth2',
    'The root directory for all the samples.')


def main(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  for dirname in os.listdir(FLAGS.sample_root):
    fulldirname = os.path.join(FLAGS.sample_root, dirname)
    if dirname in FLAGS.samples_to_skip:
      logging.debug('Skipping ' + fulldirname + ' (blacklist)')
      continue
    filelist = os.listdir(fulldirname)
    if 'settings.py' in filelist and 'manage.py' in filelist:
      logging.info(fulldirname + ' [Django]')
      proc = subprocess.Popen(
          [os.path.join(fulldirname, 'manage.py'),
          'runserver'])
      # Now just wait, because Django actually spawns a sub-process that does
      # the I/O and does something funky with stdout so we can't read it and
      # figure out when it is started.
      time.sleep(3)
      h = httplib2.Http()
      resp, content = h.request('http://localhost:8000/')
      assert(200 == resp.status)
      time.sleep(1)
      logging.debug('Django ppid: %d', proc.pid)
      # Find and kill the sub-process manage.py forked.
      findpids = subprocess.Popen(['ps', '--ppid', str(proc.pid), 'o', 'pid',],
          stdout=subprocess.PIPE)
      for p in findpids.stdout.readlines():
        if 'PID' not in p:
          os.kill(int(p), signal.SIGINT)
      os.kill(proc.pid, signal.SIGINT)
      proc.wait()
    elif 'app.yaml' in filelist:
      logging.info(fulldirname + ' [App Engine]')
      proc = subprocess.Popen(
          [os.path.join(FLAGS.app_engine_dir, 'dev_appserver.py'),
          fulldirname],
          stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT)
      line = proc.stdout.readline()
      logging.debug('READ: ' + line)
      while '] Running application' not in line:
        line = proc.stdout.readline()
        logging.debug('READ: ' + line)
      h = httplib2.Http()
      resp, content = h.request('http://localhost:8080/')
      assert(200 == resp.status)
      time.sleep(1)
      os.kill(proc.pid, signal.SIGINT)
      proc.wait()
    else:
      logging.info(fulldirname + ' [Command-line]')
      for filename in os.listdir(fulldirname):
        if filename.endswith('.py'):
          logging.info('Running: ' + filename)
          proc = subprocess.Popen(['python',
            os.path.join(fulldirname, filename)])
          returncode = proc.wait()
          assert(returncode == 0)


if __name__ == '__main__':
  main(sys.argv)
