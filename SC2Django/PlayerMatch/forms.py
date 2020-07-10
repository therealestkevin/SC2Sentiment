from django import forms


class FileFieldForm(forms.Form):
    replay_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

