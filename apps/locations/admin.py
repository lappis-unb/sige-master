from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.locations.models import Address, City, GeographicLocation, State


class CityInline(admin.TabularInline):
    model = City
    extra = 1


class StateInline(admin.TabularInline):
    model = State
    extra = 1


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("state", "name")
    search_fields = ["name"]
    list_filter = ("state",)
    autocomplete_fields = ["state"]

    fields = ("state", "name")


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "acronym")
    search_fields = ("name", "acronym")


class AddressForm(forms.ModelForm):
    state = forms.ModelChoiceField(queryset=State.objects.all(), label=_("State"))
    city_name = forms.CharField(max_length=100, label=_("City"))

    class Meta:
        model = Address
        fields = ["address", "number", "complement", "zip_code", "state", "city_name"]

    def save(self, commit=True):
        state = self.cleaned_data.get("state")
        city_name = self.cleaned_data.get("city_name")

        city, _ = City.objects.get_or_create(name=city_name, state=state)

        address = super(AddressForm, self).save(commit=False)
        address.city = city

        if commit:
            address.save()
        return address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    form = AddressForm
    list_display = ("address", "number", "city", "get_state", "zip_code")
    search_fields = ("address", "number", "city__name", "zip_code")
    list_filter = ("city__state", "city")

    def get_state(self, obj):
        return f"{obj.city.state.name}/{obj.city.state.acronym}"

    get_state.short_description = _("state")


@admin.register(GeographicLocation)
class GeographicLocationAdmin(admin.ModelAdmin):
    list_display = ("id", "latitude", "longitude", "map_type")
    list_filter = ("map_type",)
