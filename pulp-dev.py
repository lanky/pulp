#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
import optparse
import os
import sys

DIRS = (
    '/etc',
    '/etc/httpd',
    '/etc/httpd/conf.d',
    '/etc/pulp',
    '/srv',
    '/srv/juicer',
    '/var/lib/pulp',
)

LINKS = (
    'etc/pulp/juicer.ini',
    'etc/pulp/pulp.ini',
    'etc/pulp/client.ini',
    'etc/httpd/conf.d/juicer.conf',
    'srv/juicer/juicer.wsgi',
)

def parse_cmdline():
    """
    Parse and validate the command line options.
    """
    parser = optparse.OptionParser()
    
    parser.add_option('-I', '--install',
                      action='store_true',
                      help='install pulp development files')
    parser.add_option('-U', '--uninstall',
                      action='store_true',
                      help='uninstall pulp development files')
    parser.add_option('-D', '--debug',
                      action='store_true',
                      help=optparse.SUPPRESS_HELP)
    
    parser.set_defaults(install=False,
                        uninstall=False,
                        debug=False)
    
    opts, args = parser.parse_args()
    
    if opts.install and opts.uninstall:
        parser.error('both install and uninstall specified')
    
    if not (opts.install or opts.uninstall):
        parser.error('neither install or uninstall specified')
        
    return (opts, args)


def debug(opts, msg):
    if not opts.debug:
        return
    sys.stderr.write('%s\n' % msg)
    

def create_dirs(opts):
    for d in DIRS:
        debug(opts, 'creating directory: %s' % d)
        if os.path.exists(d) and os.path.isdir(d):
            debug(opts, '%s exists, skipping' % d)
            continue
        os.mkdir(d, 0777)


def install(opts):
    create_dirs(opts)
    currdir = os.path.abspath(os.path.dirname(__file__))
    for l in LINKS:
        debug(opts, 'creating link: /%s' % l)
        if os.path.exists('/'+l):
            debug(opts, '/%s exists, skipping' % l)
            continue
        os.symlink(os.path.join(currdir, l), '/'+l)

    # Link between pulp and apache
    if not os.path.exists('/var/www/html/pub'):
        os.symlink('/var/lib/pulp', '/var/www/html/pub')

    # Create the log files so apache can access them
    if not os.path.exists('/var/log/pulp'):
        os.mkdir('/var/log/pulp', 0777)

    return os.EX_OK


def uninstall(opts):
    for l in LINKS:
        debug(opts, 'removing link: /%s' % l)
        if not os.path.exists('/'+l):
            debug(opts, '/%s does not exist, skipping' % l)
            continue
        os.unlink('/'+l)

    # Link between pulp and apache
    if os.path.exists('/var/www/html/pub'):
        os.unlink('/var/www/html/pub')

    return os.EX_OK

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # TODO add something to check for permissions
    opts, args = parse_cmdline()
    if opts.install:
        sys.exit(install(opts))
    if opts.uninstall:
        sys.exit(uninstall(opts))
