from django import forms

class ChatForm(forms.Form):
    prompt = forms.CharField(max_length=255, widget=forms.Textarea)
    