"""
----------------------------------------------------------------------------

   METADATA:

       File:    document_types.py
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

from paperap.models.document_type import DocumentType, DocumentTypeQuerySet
from paperap.resources.base import BaseResource, BulkEditing, StandardResource


class DocumentTypeResource(StandardResource[DocumentType, DocumentTypeQuerySet], BulkEditing):
    """Resource for managing document types."""

    model_class = DocumentType
    queryset_class = DocumentTypeQuerySet
    name: str = "document_types"
