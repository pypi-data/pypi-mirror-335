from django.contrib import admin
from edc_action_item import action_fieldset_tuple
from edc_lab_results.admin import BloodResultsModelAdminMixin
from edc_lab_results.fieldsets import BloodResultFieldset

from ...admin_site import intecomm_subject_admin
from ...forms import BloodResultsFbcForm
from ...models import BloodResultsFbc
from ..modeladmin_mixins import CrfModelAdmin


@admin.register(BloodResultsFbc, site=intecomm_subject_admin)
class BloodResultsFbcAdmin(BloodResultsModelAdminMixin, CrfModelAdmin):
    form = BloodResultsFbcForm
    fieldsets = BloodResultFieldset(
        BloodResultsFbc.lab_panel,
        model_cls=BloodResultsFbc,
        extra_fieldsets=[(-1, action_fieldset_tuple)],
    ).fieldsets
