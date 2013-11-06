#!/usr/bin/env python

import sys
import os

def daemonize(stdin = '/dev/null', stdout = '/dev/null', stderr = '/dev/null', workdir = '/var/log/'):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)              #parent exit.
    except OSError, e:
        sys.stderr.write("Fork #1 failed: (%d) %s\n", e.errorno, e.strerror )
        sys.exit(1)

    os.chdir(workdir)
    os.umask(0)
    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)              #parent exit.
    except OSError, e:
        sys.stderr.write("Fork #2 failed: (%d) %s\n", e.errorno, e.strerror )
        sys.exit(1)
        
    for f in sys.stdout, sys.stderr:
        f.flush()

    stdi = file(stdin, 'r')
    stdo = file(stdout, 'a+')
    stde = file(stderr, 'a+', 0)
    os.dup2(stdi.fileno(), sys.stdin.fileno())
    os.dup2(stdo.fileno(), sys.stdout.fileno())
    os.dup2(stde.fileno(), sys.stderr.fileno())
    
    pass
