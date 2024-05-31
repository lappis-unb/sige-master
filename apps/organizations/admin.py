from django.contrib import admin

from apps.organizations.models import Entity, Organization


class EntityInline(admin.TabularInline):
    model = Entity
    extra = 1


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    inlines = [EntityInline]
    list_display = (
        "id",
        "name",
        "acronym",
        "entity_type",
        "description",
        "address",
        "geo_location",
        "parent",
    )
    search_fields = ("name", "acronym", "entity_type")
    autocomplete_fields = ["address"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [EntityInline]

    list_display = ("id", "name", "acronym", "entity_type", "email", "phone")
    list_filter = ("entity_type", "parent")
    search_fields = ("name", "acronym", "entity_type")
    autocomplete_fields = ["address", "parent"]
    fieldsets = (
        ("Basic Information", {"fields": ("name", "acronym", "entity_type", "parent")}),
        ("Contact Details", {"classes": ("collapse",), "fields": ("address", "phone", "email", "website")}),
        ("Additional Information", {"classes": ("collapse",), "fields": ("description", "geo_location")}),
    )
