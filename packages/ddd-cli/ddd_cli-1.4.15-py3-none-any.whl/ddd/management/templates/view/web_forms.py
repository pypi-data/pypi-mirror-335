from django import forms
from django.core import validators

class [[ entity_name.capitalize() ]]BaseForm(forms.Form):
    """
    Base Form
    """

    # Title
    title = forms.CharField(
        label='Title',
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Title',
            'class': 'title_form_[[ entity_name.lower() ]]'
        }),
        validators=[
            validators.MinLengthValidator(4, 'The title is too short'),
            validators.MaxLengthValidator(30, 'The title is too long'),
            validators.RegexValidator(
                '^[A-Za-z0-9ñÑáéíóúÁÉÍÓÚ ]*$',
                'The title format is incorrect',
                'invalid_title'
            )
        ]
    )

    # Content
    content = forms.CharField(
        label='Content',
        widget=forms.Textarea,
        validators=[
            validators.MinLengthValidator(4, 'The content is too short'),
            validators.MaxLengthValidator(30, 'The content is too long'),
            validators.RegexValidator(
                '^[A-Za-z0-9ñÑáéíóúÁÉÍÓÚ ]*$',
                'The content format is incorrect',
                'invalid_content'
            )
        ]
    )
    content.widget.attrs.update({
        'placeholder': 'Content',
        'class': 'content_form_[[ entity_name.lower() ]]',
        'id': 'content_form'
    })

    # Published
    public_options = [
        (True, 'Yes'),
        (False, 'No')
    ]
    public = forms.TypedChoiceField(
        label='Published?',
        choices=public_options
    )


class [[ entity_name.capitalize() ]]CreateForm([[ entity_name.capitalize() ]]BaseForm):
    """
    Form to create a new instance of [[ entity_name.lower() ]]. Sin modificaciones adicionales.
    """
    pass


class [[ entity_name.capitalize() ]]EditForm([[ entity_name.capitalize() ]]BaseForm):
    """
    Form to edit an instance of [[ entity_name.lower() ]]. Agregamos un campo adicional para 'id'.
    """
    id = forms.IntegerField(
        label='ID',
        required=False,
        widget=forms.HiddenInput()
    )

    
class [[ entity_name.capitalize() ]]ViewForm([[ entity_name.capitalize() ]]BaseForm):
    """
    Readonly form to view an instance of [[ entity_name.lower() ]]
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hacer todos los campos no editables
        for field in self.fields.values():
            field.widget.attrs['disabled'] = True