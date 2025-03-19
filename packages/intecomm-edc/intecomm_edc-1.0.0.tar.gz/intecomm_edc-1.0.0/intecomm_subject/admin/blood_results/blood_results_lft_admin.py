from django.contrib import admin
from edc_action_item import action_fieldset_tuple
from edc_lab_results.admin import BloodResultsModelAdminMixin
from edc_lab_results.fieldsets import BloodResultFieldset

from ...admin_site import intecomm_subject_admin
from ...forms import BloodResultsLftForm
from ...models import BloodResultsLft
from ..modeladmin_mixins import CrfModelAdmin


@admin.register(BloodResultsLft, site=intecomm_subject_admin)
class BloodResultsLftAdmin(BloodResultsModelAdminMixin, CrfModelAdmin):
    form = BloodResultsLftForm
    fieldsets = BloodResultFieldset(
        BloodResultsLft.lab_panel,
        model_cls=BloodResultsLft,
        extra_fieldsets=[
            (-1, action_fieldset_tuple),
        ],
    ).fieldsets
