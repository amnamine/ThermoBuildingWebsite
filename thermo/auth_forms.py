from __future__ import annotations

from django.contrib.auth.forms import AuthenticationForm


class ConnexionForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.setdefault("class", "form-control")
        self.fields["username"].widget.attrs.setdefault("autocomplete", "username")
        self.fields["password"].widget.attrs.setdefault("class", "form-control")
        self.fields["password"].widget.attrs.setdefault("autocomplete", "current-password")
