# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""The main pyweb executable.

This file, when executed (via the `pywebgen` stub), generates a
website by taking data out of source, optionally applying a filter,
and dropping the file in a generated output directory.
"""

__author__ = 'David Anderson <dave@natulte.net>'

import optparse
import os.path
import sys

import container
import deploy
import generator
import processors
import odict
import versions


VERSION = '0.1.0'
OPTPARSE_VERSION = '%prog ' + VERSION


def startsite_cmd(cmdline):
    STARTSITE_USAGE = '%prog startsite [-d <deploy_dir>] <site dir>'
    parser = optparse.OptionParser(usage=STARTSITE_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    parser.add_option('-d', '--deploy-dir', action='store',
                      type='string', dest='deploy_dir')
    parser.add_option('-E', '--embed-pyweb', action='store_true',
                      dest='embed_pyweb')
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 1:
        parser.print_help()
        return 2

    if os.path.exists(args[0]):
        print 'Path already exists, cannot create site.'
        return 1

    container.Container.Create(args[0], options.deploy_dir,
                               embed_pyweb=options.embed_pyweb)
    print 'Created site container in %s' % args[0]
    return 0


def generate_cmd(cmdline):
    GENERATE_USAGE = '%prog generate [options] <input dir> <output dir>'
    parser = optparse.OptionParser(usage=GENERATE_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    parser.add_option('-m', '--manifest', action='store',
                      type='string', dest='manifest')

    (options, args) = parser.parse_args(cmdline)

    if len(args) != 2:
        parser.print_help()
        return 2

    gen = generator.Generator(args[0], processors.ListProcessors())
    gen.Generate(args[1], manifest_path=options.manifest)
    return 0


def vgenerate_cmd(cmdline):
    VGENERATE_USAGE = '%prog vgenerate <input dir> <versions dir>'
    parser = optparse.OptionParser(usage=VGENERATE_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    parser.add_option('-d', '--deploy-dir', action='store',
                      type='string', dest='deploy_dir')
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 2:
        parser.print_help()
        return 2

    gen = versions.VersionnedGenerator(args[1], options.deploy_dir)
    ts, out, manifest, current = gen.Generate(args[0], processors.ListProcessors())
    if current:
        print 'Generated version %s and made current.' % ts
    else:
        print 'Generated version %s.' % ts
    return 0


def vcurrent_cmd(cmdline):
    VCURRENT_USAGE = '%prog vcurrent <versions_dir> <version>'
    parser = optparse.OptionParser(usage=VCURRENT_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    parser.add_option('-d', '--deploy-dir', action='store',
                      type='string', dest='deploy_dir')
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 2:
        parser.print_help()
        return 2

    if args[1] == 'latest':
        version = 0
    else:
        try:
            version = int(args[1])
        except ValueError:
            print 'Version must be an integer, or "latest"'
            return 2

    gen = versions.VersionnedGenerator(args[0], options.deploy_dir)
    ts = gen.ChangeCurrent(version)
    print 'Set current version to %s.' % ts
    return 0


def vinfo_cmd(cmdline):
    VINFO_USAGE = '%prog vinfo <versions_dir>'
    parser = optparse.OptionParser(usage=VINFO_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 1:
        parser.print_help()
        return 2

    gen = versions.VersionnedGenerator(args[0])
    site_versions, current = gen.Versions()

    if not site_versions:
        print 'No website versions.'
        return 0

    print 'Versions:'
    for i, ts in enumerate(site_versions):
        if ts == current:
            print '  %2d. %s (current)' % (i, ts)
        else:
            print '  %2d. %s' % (i, ts)

    return 0


def vgc_cmd(cmdline):
    VGC_USAGE = '%prog vgc <versions_dir>'
    parser = optparse.OptionParser(usage=VGC_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 1:
        parser.print_help()
        return 2

    gen = versions.VersionnedGenerator(args[0])
    gc_versions = gen.GarbageCollect()

    if not gc_versions:
        print 'Nothing to garbage collect or no current version to base from.'
    else:
        print 'Garbage collected %d versions:' % len(gc_versions)
        print '\n'.join(['  %s' % v for v in gc_versions])

    return 0


def deploy_cmd(cmdline):
    DEPLOY_USAGE = ('%prog deploy <webgen output dir> '
                    '<deploy dir> <webgen manifest>')
    parser = optparse.OptionParser(usage=DEPLOY_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 3:
        parser.print_help()
        return 2

    deploy.Deploy(args[0], args[1], args[2])
    return 0


def undeploy_cmd(cmdline):
    UNDEPLOY_USAGE = ('%prog undeploy <webgen output dir> '
                      '<deploy dir> <webgen manifest>')
    parser = optparse.OptionParser(usage=UNDEPLOY_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 3:
        parser.print_help()
        return 2

    deploy.Undeploy(args[0], args[1], args[2])
    return 0


COMMANDS = odict.OrderedDict((
        ('startsite', startsite_cmd),
        ('generate', generate_cmd),
        ('vgenerate', vgenerate_cmd),
        ('vcurrent', vcurrent_cmd),
        ('vinfo', vinfo_cmd),
        ('vgc', vgc_cmd),
        ('deploy', deploy_cmd),
        ('undeploy', undeploy_cmd)))


def main():
    USAGE = ('%prog <command> [options] <command args>\n\nCommands:\n  ' +
             '\n  '.join(COMMANDS.keys()))
    parser = optparse.OptionParser(usage=USAGE, version=OPTPARSE_VERSION)
    parser.disable_interspersed_args()
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        return 2

    if args[0] not in COMMANDS:
        print 'No such command.\n'
        parser.print_help()
        return 2

    return COMMANDS[args[0]](args[1:])
