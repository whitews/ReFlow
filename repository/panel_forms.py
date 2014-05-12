from django import forms
from repository.models import SitePanel


class EditSitePanelForm(forms.ModelForm):
    class Meta:
        model = SitePanel
        exclude = ('project_panel',)
