from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class UploadFileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({
            'accept': '.tif,.tiff',
            'class': 'file-input',
            'multiple': True
        })


    file = MultipleFileField(
        label='',
        help_text='Select one or more TIFF files (max 100MB each)'
    )

    def clean_file(self):
        files = self.cleaned_data.get('file', [])
        if not files:
            raise forms.ValidationError("Please select at least one file.")
            
        cleaned_files = []
        for file in files:
            if file:
                if file.size > 100 * 1024 * 1024:  
                    raise forms.ValidationError(f"File '{file.name}' is too large (max 100MB)")
                if not file.name.lower().endswith(('.tif', '.tiff')):
                    raise forms.ValidationError(f"File '{file.name}' is not a TIFF file")
                cleaned_files.append(file)
        return cleaned_files