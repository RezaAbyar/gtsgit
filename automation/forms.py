from django import forms
from base.models import Owner, Role
from .models import Message, WordTemplate


class MessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Message
        fields = ['subject', 'body', 'image', 'recipients', 'groups', 'files']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'files': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)


    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sender = self.sender

        if commit:
            instance.save()
            self.save_m2m()

        return instance