from django import forms

from .models import Evidencia, Recomendacion, Responsable


class RecomendacionForm(forms.ModelForm):
    responsables = forms.ModelMultipleChoiceField(
        queryset=Responsable.objects.filter(activo=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Responsables",
    )

    class Meta:
        model = Recomendacion
        fields = [
            "codigo",
            "descripcion",
            "origen",
            "prioridad",
            "estado",
            "fecha_emision",
            "fecha_limite",
        ]
        widgets = {
            "fecha_emision": forms.DateInput(attrs={"type": "date"}),
            "fecha_limite": forms.DateInput(attrs={"type": "date"}),
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault("class", "campo")
        self.fields["responsables"].widget.attrs["class"] = "campo-checkbox"
        if self.instance.pk:
            self.fields["responsables"].initial = self.instance.responsables.all()


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        fields = ["archivo", "tipo", "descripcion"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault("class", "campo")
