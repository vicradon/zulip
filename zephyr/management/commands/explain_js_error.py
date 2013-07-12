from __future__ import absolute_import

import os
import sys
import select

from django.core.management.base import BaseCommand, CommandError

from zephyr.lib.unminify import SourceMap

# Wait for the user to paste text, then time out quickly and
# return it.  Disable echo so that we can re-echo the same
# lines with our annotations.
def get_full_paste():
    try:
        os.system('stty -echo raw isig')

        data = ''
        while True:
            fd = sys.stdin.fileno()
            can_read = select.select([fd], [], [], 0.1)[0]
            if can_read:
                data += os.read(fd, 1)
            else:
                if data:
                    return data
    finally:
        os.system('stty cooked echo')

class Command(BaseCommand):
    args = '<source map directory>'
    help = '''Add source locations to a stack backtrace generated by minified code.

The currently checked out code should match the version that generated the error.'''

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('No source map directory specified')

        source_map = SourceMap(args[0])

        if os.isatty(sys.stdin.fileno()):
            sys.stdout.write('Paste stacktrace:\n\n')
            sys.stdout.flush()
            stacktrace = get_full_paste()
        else:
            stacktrace = sys.stdin.read()

        sys.stdout.write(source_map.annotate_stacktrace(stacktrace))
