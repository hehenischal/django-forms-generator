from bs4 import BeautifulSoup

def html_to_django_form(html_code, form_name="GeneratedForm"):
    soup = BeautifulSoup(html_code, "html.parser")

    # Collect labels
    labels = {}
    for label in soup.find_all("label"):
        target = label.get("for")
        if target:
            labels[target] = label.text.strip()

    fields = []

    for tag in soup.find_all(["input", "textarea", "select"]):
        field_name = tag.get("name")
        if not field_name:
            continue  

        field_required = tag.has_attr("required")
        field_type = tag.get("type", "text")
        field_id = tag.get("id")

        # Find label text
        if field_id and field_id in labels:
            field_label = labels[field_id]
        elif tag.get("placeholder"):
            field_label = tag.get("placeholder")
        else:
            field_label = field_name.capitalize()

        # Build attrs dictionary
        attrs = {}
        if tag.get("class"):
            attrs["class"] = " ".join(tag.get("class"))
        if tag.get("id"):
            attrs["id"] = tag.get("id")
        if tag.get("placeholder"):
            attrs["placeholder"] = tag.get("placeholder")

        attrs_str = f", widget=forms.TextInput(attrs={attrs})" if attrs else ""

        # Map fields
        if tag.name == "textarea":
            widget_str = f"forms.Textarea(attrs={attrs})" if attrs else "forms.Textarea"
            field = f'{field_name} = forms.CharField(label="{field_label}", widget={widget_str}, required={field_required})'

        elif tag.name == "select":
            options = [(opt.get("value", opt.text), opt.text) for opt in tag.find_all("option")]
            multiple = tag.has_attr("multiple")
            widget_str = "forms.SelectMultiple" if multiple else "forms.Select"
            widget_str = f"{widget_str}(attrs={attrs})" if attrs else widget_str
            field_type_str = "MultipleChoiceField" if multiple else "ChoiceField"
            field = f'{field_name} = forms.{field_type_str}(label="{field_label}", choices={options}, widget={widget_str}, required={field_required})'

        else:  # input
            if field_type == "text":
                max_len = tag.get("maxlength", 100)
                widget_str = f"forms.TextInput(attrs={attrs})" if attrs else "forms.TextInput"
                field = f'{field_name} = forms.CharField(label="{field_label}", max_length={max_len}, widget={widget_str}, required={field_required})'

            elif field_type == "email":
                widget_str = f"forms.EmailInput(attrs={attrs})" if attrs else "forms.EmailInput"
                field = f'{field_name} = forms.EmailField(label="{field_label}", widget={widget_str}, required={field_required})'

            elif field_type == "password":
                widget_str = f"forms.PasswordInput(attrs={attrs})" if attrs else "forms.PasswordInput"
                field = f'{field_name} = forms.CharField(label="{field_label}", widget={widget_str}, required={field_required})'

            elif field_type == "number":
                widget_str = f"forms.NumberInput(attrs={attrs})" if attrs else "forms.NumberInput"
                field = f'{field_name} = forms.IntegerField(label="{field_label}", widget={widget_str}, required={field_required})'

            elif field_type == "checkbox":
                widget_str = f"forms.CheckboxInput(attrs={attrs})" if attrs else "forms.CheckboxInput"
                field = f'{field_name} = forms.BooleanField(label="{field_label}", widget={widget_str}, required={field_required})'

            elif field_type == "radio":
                radios = soup.find_all("input", {"type": "radio", "name": field_name})
                choices = [(r.get("value"), r.get("value")) for r in radios]
                widget_str = f"forms.RadioSelect(attrs={attrs})" if attrs else "forms.RadioSelect"
                field = f'{field_name} = forms.ChoiceField(label="{field_label}", choices={choices}, widget={widget_str}, required={field_required})'

            elif field_type == "date":
                widget_str = f"forms.DateInput(attrs={attrs})" if attrs else "forms.DateInput"
                field = f'{field_name} = forms.DateField(label="{field_label}", widget={widget_str}, required={field_required})'

            elif field_type == "datetime-local":
                widget_str = f"forms.DateTimeInput(attrs={attrs})" if attrs else "forms.DateTimeInput"
                field = f'{field_name} = forms.DateTimeField(label="{field_label}", widget={widget_str}, required={field_required})'

            elif field_type == "time":
                widget_str = f"forms.TimeInput(attrs={attrs})" if attrs else "forms.TimeInput"
                field = f'{field_name} = forms.TimeField(label="{field_label}", widget={widget_str}, required={field_required})'

            elif field_type == "file":
                widget_str = f"forms.ClearableFileInput(attrs={attrs})" if attrs else "forms.ClearableFileInput"
                field = f'{field_name} = forms.FileField(label="{field_label}", widget={widget_str}, required={field_required})'

            else:
                widget_str = f"forms.TextInput(attrs={attrs})" if attrs else "forms.TextInput"
                field = f'{field_name} = forms.CharField(label="{field_label}", widget={widget_str}, required={field_required})'

        fields.append(field)

    # Wrap in form
    output = "from django import forms\n\n"
    output += f"class {form_name}(forms.Form):\n"
    if fields:
        for f in fields:
            output += f"    {f}\n"
    else:
        output += "    pass\n"

    return output