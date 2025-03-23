"""
----------------------------------------------------------------------------

   METADATA:

       File:    profile.py
        Project: paperap
       Created: 2025-03-04
        Version: 0.0.8
       Author:  Jess Mann
       Email:   jess@jmann.me
        Copyright (c) 2025 Jess Mann

----------------------------------------------------------------------------

   LAST MODIFIED:

       2025-03-04     By Jess Mann

"""

from __future__ import annotations

from paperap.models.profile import Profile, ProfileQuerySet
from paperap.resources.base import BaseResource, StandardResource


class ProfileResource(StandardResource[Profile, ProfileQuerySet]):
    """Resource for managing profiles."""

    model_class = Profile
    queryset_class = ProfileQuerySet
    name: str = "profile"
