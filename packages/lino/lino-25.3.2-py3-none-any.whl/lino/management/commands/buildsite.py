# -*- coding: UTF-8 -*-
# Copyright 2009-2023 Rumma & Ko Ltd.
# License: GNU Affero General Public License v3 (see file COPYING for details)

from click import confirm
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
from lino import logger


class Command(BaseCommand):
    """Run install, buildcache, collectstatic and makehelp after pull."""

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--noinput",
            action="store_false",
            dest="interactive",
            default=True,
            help="Do not prompt for input of any kind.",
        ),

    def handle(self, *args, **options):
        interactive = options.get("interactive")
        verbosity = options.get("verbosity")
        project_dir = settings.SITE.project_dir

        if interactive:
            msg = "Build everything for ({})".format(project_dir)
            msg += ".\nAre you sure?"
            if not confirm(msg, default=True):
                raise CommandError("User abort.")

        # the following log message was useful on Travis 20150104
        if verbosity > 0:
            logger.info("`buildsite` started on %s.", project_dir)

        pth = project_dir / "settings.py"
        if pth.exists():
            pth.touch()

        options = dict(interactive=False, verbosity=verbosity)

        call_command("install", **options)
        call_command("collectstatic", **options)
        call_command("buildcache", verbosity=verbosity)
        if settings.SITE.is_installed("help"):
            call_command("makehelp", verbosity=verbosity)

        # for p in settings.SITE.installed_plugins:
        #     p.on_buildsite(settings.SITE, verbosity=verbosity)

        settings.SITE.clear_site_config()

        logger.info("`buildsite` finished on %s.", project_dir)
