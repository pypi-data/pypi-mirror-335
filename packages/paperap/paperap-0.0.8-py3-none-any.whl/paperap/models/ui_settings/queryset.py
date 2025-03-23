"""
----------------------------------------------------------------------------

   METADATA:

       File:    queryset.py
        Project: paperap
       Created: 2025-03-04
        Version: 0.0.5
       Author:  Jess Mann
       Email:   jess@jmann.me
        Copyright (c) 2025 Jess Mann

----------------------------------------------------------------------------

   LAST MODIFIED:

       2025-03-04     By Jess Mann

"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Self

from paperap.models.abstract.queryset import BaseQuerySet, StandardQuerySet

if TYPE_CHECKING:
    from paperap.models.ui_settings.model import UISettings

logger = logging.getLogger(__name__)


class UISettingsQuerySet(StandardQuerySet["UISettings"]):
    """
    A lazy-loaded, chainable query interface for Paperless NGX resources.

    BaseQuerySet provides pagination, filtering, and caching functionality similar to Django's BaseQuerySet.
    It's designed to be lazy - only fetching data when it's actually needed.
    """

    def has_permission(self, value: str) -> Self:
        """
        Filter UI settings by permissions.

        Args:
            value (str): The permissions to filter by

        Returns:
            UISettingsQuerySet: The filtered queryset

        """
        return self.filter(permissions__contains=value)
