import json
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


def get_vite_assets():
    manifest_path = settings.FRONTEND_MANIFEST_PATH
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    return manifest
