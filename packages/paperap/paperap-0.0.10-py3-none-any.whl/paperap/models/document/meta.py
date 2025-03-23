"""




----------------------------------------------------------------------------

METADATA:

File:    meta.py
        Project: paperap
Created: 2025-03-22
        Version: 0.0.10
Author:  Jess Mann
Email:   jess@jmann.me
        Copyright (c) 2025 Jess Mann

----------------------------------------------------------------------------

LAST MODIFIED:

2025-03-22     By Jess Mann

"""

SUPPORTED_FILTERING_PARAMS = {
    "id__in",
    "id",
    "title__istartswith",
    "title__iendswith",
    "title__icontains",
    "title__iexact",
    "content__istartswith",
    "content__iendswith",
    "content__icontains",
    "content__iexact",
    "archive_serial_number",
    "archive_serial_number__gt",
    "archive_serial_number__gte",
    "archive_serial_number__lt",
    "archive_serial_number__lte",
    "archive_serial_number__isnull",
    "content__contains",  # maybe?
    "correspondent__isnull",
    "correspondent__id__in",
    "correspondent__id",
    "correspondent__name__istartswith",
    "correspondent__name__iendswith",
    "correspondent__name__icontains",
    "correspondent__name__iexact",
    "correspondent__slug__iexact",  # maybe?
    "created__year",
    "created__month",
    "created__day",
    "created__date__gt",
    "created__gt",
    "created__date__lt",
    "created__lt",
    "added__year",
    "added__month",
    "added__day",
    "added__date__gt",
    "added__gt",
    "added__date__lt",
    "added__lt",
    "original_filename__istartswith",
    "original_filename__iendswith",
    "original_filename__icontains",
    "original_filename__iexact",
    "checksum__istartswith",
    "checksum__iendswith",
    "checksum__icontains",
    "checksum__iexact",
    "tags__id__in",
    "tags__id",
    "tags__name__istartswith",
    "tags__name__iendswith",
    "tags__name__icontains",
    "tags__name__iexact",
    "document_type__isnull",
    "document_type__id__in",
    "document_type__id",
    "document_type__name__istartswith",
    "document_type__name__iendswith",
    "document_type__name__icontains",
    "document_type__name__iexact",
    "storage_path__isnull",
    "storage_path__id__in",
    "storage_path__id",
    "storage_path__name__istartswith",
    "storage_path__name__iendswith",
    "storage_path__name__icontains",
    "storage_path__name__iexact",
    "owner__isnull",
    "owner__id__in",
    "owner__id",
    "is_tagged",
    "tags__id__all",
    "tags__id__none",
    "correspondent__id__none",
    "document_type__id__none",
    "storage_path__id__none",
    "is_in_inbox",
    "title_content",
    "owner__id__none",
    "custom_fields__icontains",
    "custom_fields__id__all",
    "custom_fields__id__none",  # ??
    "custom_fields__id__in",
    "custom_field_query",  # ??
    "has_custom_fields",
    "shared_by__id",
    "shared_by__id__in",
}
