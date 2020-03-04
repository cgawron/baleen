# baleen.console.commands.summary
# A utility to print out information about the Baleen state.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 11:08:57 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: summary.py [da54aa8] benjamin@bengfort.com $

"""
A utility to print out information about the Baleen state.
"""

##########################################################################
## Imports
##########################################################################

import baleen
import baleen.models as db

from commis import Command
from baleen.config import settings
from baleen.utils.timez import HUMAN_DATETIME

##########################################################################
## Command
##########################################################################

class SummaryCommand(Command):

    name = 'info'
    help = 'print info about Baleen from the database'
    args = {
        ('-c', '--config'): {
            'action': 'store_true',
            'default': False,
            'help': 'Also print the configuration',
        }
    }

    def handle(self, args):
        # Setup output and connect to database.
        output = []
        db.connect()

        # Printout configuration details as necessary.
        if args.config:
            output.append("Configuration:")
            output.append(str(settings))
            output.append("")

        output.append("Baleen v{} Status:".format(baleen.get_version()))
        output.append(
            "{} Feeds and {} Posts after {} Jobs".format(
                db.Feed.objects.count(),
                db.Post.objects.count(),
                db.Job.objects.count(),
            )
        )

        latest = db.Job.objects.order_by('-started').first()
        output.extend([
            "",
            "Latest Job: ",
            "    Type: {} v{}".format(latest.name, latest.version),
            "    Job ID: {}".format(latest.jobid),
            "    Started: {}".format(latest.started.strftime(HUMAN_DATETIME))
        ])

        if latest.finished:
            if latest.failed:
                output.append("    Failed: {}".format(latest.reason))
            else:
                output.append("    Finished: {}".format(latest.finished.strftime(HUMAN_DATETIME)))
                output.append("    Counts:")
                output.append("      " + "\n      ".join(["{}: {}".format(*item) for item in list(latest.counts.items())]))
                output.append("    Errors:")
                output.append("      " + "\n      ".join(["{}: {}".format(*item) for item in list(latest.errors.items())]))
        else:
            output.append("    Currently Running")

        latest = db.Feed.objects.order_by('-updated').first()
        output.extend([
            "",
            "Latest Feed: ",
            "    Title: \"{}\"".format(latest.title),
            "    eTag: \"{}\"".format(latest.etag),
            "    Modified: {}".format(latest.modified),
            "    Updated: {}".format(latest.updated.strftime(HUMAN_DATETIME)),
            # u"    Posts: {}".format(latest.count_posts()), # This is very slow need to fix.
        ])

        latest = db.Post.objects.order_by('-id').first()
        output.extend([
            "",
            "Latest Post: ",
            "    Title: \"{}\"".format(latest.title),
            "    Feed: \"{}\"".format(latest.feed.title),
            "    Fetched: {}".format(latest.created.strftime(HUMAN_DATETIME)),
        ])

        return "\n".join(output).encode('utf-8', errors='replace')
