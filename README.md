# django-forms-generator
This repo contains code for Django forms generator that gives out django form classes from html code

## Input 

```python
str = '''<label for="username">Enter username </label>
<input type="text" name="username" id="username">
'''
html_to_django_forms(str)
```

## Output
```python
from django import forms

class GeneratedForm(forms.Form):
    username = forms.CharField(
                      label="Enter username",
                      max_length=100,
                      widget=forms.TextInput(
                                              attrs={'id': 'username'}),
                                              required=False)
```
