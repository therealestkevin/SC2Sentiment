from django import forms
from .validators import validate_file_extension


class FileFieldForm(forms.Form):
    replay_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                  validators=[validate_file_extension])


