from wowool.document.document import Document
from wowool.io.console import AppConsole
import logging
import sys

logger = logging.getLogger(__name__)


def print_diagnostics(doc: Document, console: AppConsole = None, file=sys.stderr):
    if console == None:
        from wowool.io.console import console

    for app_id in doc.app_ids():
        if doc.has_diagnostics(app_id):
            console.print(f"diagnostics={app_id} ", file=file)
            for item in doc.diagnostics(app_id):
                console.print("  " + item.rich(), file=file)


def log_diagnostics(doc: Document):
    for app_id in doc.app_ids():
        if doc.has_diagnostics(app_id):
            for item in doc.diagnostics(app_id):
                logger.log(item.type, f"{app_id}: {item.message}")
