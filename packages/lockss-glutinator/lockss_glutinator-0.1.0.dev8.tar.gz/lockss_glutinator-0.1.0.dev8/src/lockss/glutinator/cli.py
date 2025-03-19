#!/usr/bin/env python3

# Copyright (c) 2000-2025, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
from pathlib import Path
import rich_argparse

import lockss.glutinator
from . import __copyright__, __license__, __version__
from .app import GlutinatorApp

class GlutinatorCli(object):

    PROG = 'glutinator'

    def __init__(self):
        super().__init__()
        self._app = GlutinatorApp()
        self._args = None

    def run(self):
        self._make_parser()
        self._args = self._parser.parse_args()
        if self._args.debug_cli:
            print(self._args)
        self._args.fun()

    def _copyright(self):
        print(__copyright__)

    def _generate_static_site(self):
        self._app.generate_static_site(self._args.inventory,
                                       base_url=self._args.base_url,
                                       # conffile=self._args.configuration,
                                       outdir=self._args.output_directory)

    def _license(self):
        print(__license__)

    def _make_option_base_url(self, container):
        container.add_argument('--base-url', '-b',
                               metavar='URL',
                               help='set the base URL for <meta> tags with mandatory absolute URLs',
                               required=True)

    def _make_option_configuration(self, container):
        container.add_argument('--configuration', '-c',
                               metavar='FILE',
                               type=Path,
                               default='glutinator.yaml',
                               help='read configuration from FILE (default: %(default)s)')

    def _make_option_debug_cli(self, container):
        container.add_argument('--debug-cli',
                               action='store_true',
                               help='print the result of parsing command line arguments')

    def _make_option_input_directory(self, container, default, help):
        container.add_argument('--input-directory', '-I',
                               metavar='DIR',
                               type=Path,
                               default=default,
                               help=help)

    def _make_option_inventory(self, container):
        container.add_argument('--inventory', '-i',
                               metavar='FILE',
                               type=Path,
                               help='read inventory from FILE',
                               required=True)

    def _make_option_output_directory(self, container, default, help):
        container.add_argument('--output-directory', '-O',
                               metavar='DIR',
                               type=Path,
                               default=default,
                               help=help)

    def _make_parser(self):
        for cls in [rich_argparse.RichHelpFormatter]:
            cls.styles.update({
                'argparse.args': f'bold {cls.styles["argparse.args"]}',
                'argparse.groups': f'bold {cls.styles["argparse.groups"]}',
                'argparse.metavar': f'bold {cls.styles["argparse.metavar"]}',
                'argparse.prog': f'bold {cls.styles["argparse.prog"]}',
            })
        self._parser = argparse.ArgumentParser(prog=GlutinatorCli.PROG,
                                               formatter_class=rich_argparse.RichHelpFormatter)
        self._subparsers = self._parser.add_subparsers(title='commands',
                                                       description="Add --help to see the command's own help message.",
                                                       # With subparsers, metavar is also used as the heading of the column of subcommands
                                                       metavar='COMMAND',
                                                       # With subparsers, help is used as the heading of the column of subcommand descriptions
                                                       help='DESCRIPTION')
        self._make_option_debug_cli(self._parser)
        self._make_parser_copyright(self._subparsers)
        self._make_parser_generate_static_site(self._subparsers)
        self._make_parser_license(self._subparsers)
        self._make_parser_unpack_sources(self._subparsers)
        self._make_parser_usage(self._subparsers)
        self._make_parser_version(self._subparsers)

    def _make_parser_copyright(self, container):
        parser = container.add_parser('copyright',
                                      description='Show copyright and exit.',
                                      help='show copyright and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._copyright)

    def _make_parser_generate_static_site(self, container):
        parser = container.add_parser('generate-static-site', aliases=['gss'],
                                      description='Generate static site from sources.',
                                      help='generate static site from sources',
                                      formatter_class=self._parser.formatter_class)
        # Mandatory options
        self._make_option_base_url(parser)
        self._make_option_inventory(parser)
        # Options
        self._make_option_configuration(parser)
        self._make_option_output_directory(parser,
                                           GlutinatorApp.DEFAULT_GENERATE_STATIC_SITE_OUTPUT_DIRECTORY,
                                           'generate the static site into %(metavar)s (default: %(default)s)')
        parser.set_defaults(fun=self._generate_static_site)

    def _make_parser_license(self, container):
        parser = container.add_parser('license',
                                      description='Show license and exit.',
                                      help='show license and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._license)

    def _make_parser_unpack_sources(self, container):
        parser = container.add_parser('unpack-sources', aliases=['us'],
                                      description='Re-assemble and unpack source directories.',
                                      help='re-assemble and unpack source directories',
                                      formatter_class=self._parser.formatter_class)
        self._make_option_configuration(parser)
        self._make_option_input_directory(parser,
                                          GlutinatorApp.DEFAULT_UNPACK_SOURCES_INPUT_DIRECTORY,
                                          'unpack the sources from %(metavar)s (default: %(default)s)')
        self._make_option_output_directory(parser,
                                           GlutinatorApp.DEFAULT_UNPACK_SOURCES_OUTPUT_DIRECTORY,
                                           'unpack the sources into %(metavar)s (default: %(default)s)')
        parser.set_defaults(fun=self._unpack_sources)

    def _make_parser_usage(self, container):
        parser = container.add_parser('usage',
                                      description='Show detailed usage and exit.',
                                      help='show detailed usage and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._usage)

    def _make_parser_version(self, container):
        parser = container.add_parser('version',
                                      description='Show version and exit.',
                                      help='show version and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._version)

    def _unpack_sources(self):
        self._app.unpack_sources(conffile=self._args.configuration,
                                 indir=self._args.input_directory,
                                 outdir=self._args.output_directory)

    def _usage(self):
        self._parser.print_usage()
        print()
        uniq = set()
        for cmd, par in self._subparsers.choices.items():
            if par not in uniq:
                uniq.add(par)
                for s in par.format_usage().split('\n'):
                    usage = 'usage: '
                    print(f'{" " * len(usage)}{s[len(usage):]}' if s.startswith(usage) else s)

    def _version(self):
        print(__version__)

def main():
    GlutinatorCli().run()

if __name__ == '__main__':
    main()
