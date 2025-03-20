# -*- coding: UTF-8 -*-
# Copyright 2022-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# import time
import os
import asyncio

from django.conf import settings
from django.core.management import BaseCommand, call_command
from lino.api import dd, rt
from lino.modlib.linod.mixins import start_log_server, start_task_runner
from lino.core.requests import BaseRequest

if dd.plugins.linod.use_channels:
    import threading
    from channels.layers import get_channel_layer
    from lino.modlib.linod.utils import CHANNEL_NAME


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            help="Force starts the runworker process even if a log_socket_file exists."
            " Use only in production server.",
            action="store_true",
            default=False,
        )
        # parser.add_argument("--skip-system-tasks",
        #                     help="Skips the system tasks coroutine",
        #                     action="store_true",
        #                     default=False)

    def handle(self, *args, **options):
        log_sock_path = settings.SITE.log_sock_path

        if log_sock_path and log_sock_path.exists():
            if options.get("force"):
                log_sock_path.unlink()
            else:
                raise Exception(
                    f"log socket already exists: {log_sock_path}\n"
                    "It's probable that a worker process is already running. "
                    "Try: 'ps awx | grep linod' OR 'sudo supervisorctl status | grep worker'\n"
                    "Or the last instance of the worker process did not finish properly. "
                    "In that case remove the file and run this command again."
                )

        if not dd.plugins.linod.use_channels:
            # print("20240424 Run Lino daemon without channels")

            async def main():
                try:
                    u = await settings.SITE.user_model.objects.aget(
                        username=settings.SITE.plugins.linod.daemon_user)
                except settings.SITE.user_model.DoesNotExist:
                    u = None
                ar = BaseRequest(user=u)
                # ar = rt.login(dd.plugins.linod.daemon_user)
                await asyncio.gather(start_log_server(), start_task_runner(ar))
                # t1 = asyncio.create_task(settings.SITE.start_log_server())
                # t2 = asyncio.create_task(start_task_runner(ar))
                # await t1
                # await t2

            asyncio.run(main())

        else:
            # print("20240424 Run Lino daemon using channels")

            def start_channels():
                try:
                    asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    # loop.set_debug(True)
                    asyncio.set_event_loop(loop)
                call_command("runworker", CHANNEL_NAME)

            worker_thread = threading.Thread(target=start_channels)
            worker_thread.start()

            async def initiate_linod():
                layer = get_channel_layer()
                # if log_sock_path is not None:
                await layer.send(CHANNEL_NAME, {"type": "log.server"})
                # await asyncio.sleep(1)
                await layer.send(CHANNEL_NAME, {"type": "run.background.tasks"})

            # print("20240108 a")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(initiate_linod())
            # print("20240108 c")

            try:
                worker_thread.join()
            except KeyboardInterrupt:
                print("Finishing thread...")
                worker_thread.join(0)
