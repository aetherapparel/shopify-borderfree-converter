#!/usr/local/bin/python

import inspect
import sys

import gflags as flags

def run():
  argv = sys.argv
  try:
    # parse flags
    other_argv = flags.FLAGS(argv)

    # get main function from previous call frame
    user_main = inspect.currentframe().f_back.f_locals['main']
    user_main(other_argv)

  except flags.FlagsError, e:
    print '%s\n\nUsage: %s ARGS\n%s' % (e, sys.argv[0], flags.FLAGS)
    sys.exit(1)