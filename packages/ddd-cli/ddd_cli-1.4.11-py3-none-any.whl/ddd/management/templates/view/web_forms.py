from django import forms
from django.core import validators

class [[ entity_name.capitalize() ]]Form(forms.Form):
    """
    Form to create a new instance of [[ entity_name.lower() ]].
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


class [[ entity_name.capitalize() ]]EditForm(forms.Form):
    """
    Form to edit an existing instance of [[ entity_name.lower() ]].
    """

    # ID
    id = forms.IntegerField(
        label='ID',
        widget=forms.HiddenInput()
    )

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
            validators.MinLengthValidator(4, 'The content is too short'),
            validators.MaxLengthValidator(30, 'The content is too long'),            
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


class [[ entity_name.capitalize() ]]ViewForm(forms.Form):
    """
    Read-only form to view an instance of [[ entity_name.lower() ]].
    """

    # Title
    title = forms.CharField(
        label='Title',
        widget=forms.TextInput(attrs={
            'placeholder': 'Title',
            'class': 'title_form_[[ entity_name.lower() ]]',
            'readonly': 'readonly'
        })
    )

    # Content
    content = forms.CharField(
        label='Content',
        widget=forms.Textarea(attrs={
            'readonly': 'readonly',
            'class': 'content_form_[[ entity_name.lower() ]]'
        })
    )

    # Published
    public_options = [
        (True, 'Yes'),
        (False, 'No')
    ]
    public = forms.TypedChoiceField(
        label='Published?',
        choices=public_options,
        widget=forms.Select(attrs={
            'disabled': 'disabled'
        })
    )
