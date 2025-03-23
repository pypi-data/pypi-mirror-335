"""
----------------------------------------------------------------------------

   METADATA:

       File:    queryset.py
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

import logging
from typing import TYPE_CHECKING, Any, Self, Union

from paperap.models.abstract.queryset import BaseQuerySet, StandardQuerySet
from paperap.models.mixins.queryset import HasStandard

if TYPE_CHECKING:
    from paperap.models.tag.model import Tag

logger = logging.getLogger(__name__)


class TagQuerySet(StandardQuerySet["Tag"], HasStandard):
    """
    QuerySet for Paperless-ngx tags with specialized filtering methods.
    """

    def colour(self, value: str | int, *, exact: bool = True, case_insensitive: bool = True) -> Self:
        """
        Filter tags by color.

        Args:
            value: The color to filter by (string or integer)
            exact: If True, match the exact color, otherwise use contains
            case_insensitive: If True, ignore case when matching (for string values)

        Returns:
            Filtered TagQuerySet

        """
        if isinstance(value, int):
            return self.filter(colour=value)
        return self.filter_field_by_str("colour", value, exact=exact, case_insensitive=case_insensitive)

    def match(self, value: str, *, exact: bool = True, case_insensitive: bool = True) -> Self:
        """
        Filter tags by match value.

        Args:
            value: The value to filter by
            exact: If True, match the exact value, otherwise use contains
            case_insensitive: If True, ignore case when matching

        Returns:
            Filtered TagQuerySet

        """
        return self.filter_field_by_str("match", value, exact=exact, case_insensitive=case_insensitive)

    def matching_algorithm(self, value: int) -> Self:
        """
        Filter tags by matching algorithm.

        Args:
            value (int): The matching algorithm to filter by

        Returns:
            Filtered TagQuerySet

        """
        return self.filter(matching_algorithm=value)

    def case_insensitive(self, value: bool = True) -> Self:
        """
        Filter tags by case insensitivity.

        Args:
            value: If True, filter tags that are case insensitive

        Returns:
            Filtered TagQuerySet

        """
        return self.filter(is_insensitive=value)

    def is_inbox_tag(self, value: bool = True) -> Self:
        """
        Filter tags by inbox status.

        Args:
            value: If True, get inbox tags, otherwise non-inbox tags

        Returns:
            Filtered TagQuerySet

        """
        return self.filter(is_inbox_tag=value)

    def user_can_change(self, value: bool = True) -> Self:
        """
        Filter tags by user change permission.

        Args:
            value: If True, get tags that can be changed by user

        Returns:
            Filtered TagQuerySet

        """
        return self.filter(user_can_change=value)
