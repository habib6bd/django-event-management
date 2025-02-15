from django import forms
from events.models import Event, Participant

# Styled Form Mixin
class StyledFormMixin:
    """ Mixin to apply style to form fields """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets() 

    default_classes = "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-blue-500 focus:ring-blue-500, mb-4"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': f"{self.default_classes} resize-none",
                    'placeholder': f"Enter {field.label.lower()}",
                    'rows': 4
                })
            elif isinstance(field.widget, (forms.DateInput, forms.TimeInput)):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'type': 'date' if isinstance(field.widget, forms.DateInput) else 'time'
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': self.default_classes
                })
            else:
                field.widget.attrs.update({
                    'class': self.default_classes
                })


# Event Model Form with Styling
class EventForm(StyledFormMixin, forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=Participant.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'border-2 border-gray-300 w-full p-3 rounded-lg'}),  
        required=False
    )

    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category', 'participants']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }



