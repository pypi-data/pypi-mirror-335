"""
----------------------------------------------------------------------------

   METADATA:

       File:    correspondents.py
        Project: paperap
       Created: 2025-03-04
        Version: 0.0.9
       Author:  Jess Mann
       Email:   jess@jmann.me
        Copyright (c) 2025 Jess Mann

----------------------------------------------------------------------------

   LAST MODIFIED:

       2025-03-04     By Jess Mann

"""

from __future__ import annotations

from paperap.models.correspondent import Correspondent, CorrespondentQuerySet
from paperap.resources.base import BaseResource, BulkEditing, StandardResource


class CorrespondentResource(StandardResource[Correspondent, CorrespondentQuerySet], BulkEditing):
    """Resource for managing correspondents."""

    model_class = Correspondent
    queryset_class = CorrespondentQuerySet
    name: str = "correspondents"
