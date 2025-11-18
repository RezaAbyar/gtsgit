from django import forms
from base.models import Permission, Role, Refrence, AccessRole, DefaultPermission


class RecoverForm(forms.Form):
    code = forms.CharField(max_length=10, min_length=10)

class RolePermissionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # دریافت تمام دسترسی‌های موجود
        permissions = Permission.objects.all()

        for permission in permissions:
            field_name = f"permission_{permission.id}"
            self.fields[field_name] = forms.ChoiceField(
                choices=self.get_access_choices(),
                label=permission.info,
                required=False,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    def get_access_choices(self):
        """گزینه‌های دسترسی"""
        return [
            ('no', 'عدم دسترسی'),
            ('read', 'خواندن'),
            ('write', 'نوشتن'),
            ('edit', 'ویرایش'),
            ('full', 'دسترسی کامل'),
        ]


class DefaultPermissionForm(forms.ModelForm):
    class Meta:
        model = DefaultPermission
        fields = ['role', 'semat', 'permission', 'accessrole']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'semat': forms.Select(attrs={'class': 'form-control'}),
            'permission': forms.Select(attrs={'class': 'form-control'}),
            'accessrole': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'role': 'نقش',
            'semat': 'سمت',
            'permission': 'دسترسی',
            'accessrole': 'سطح دسترسی',
        }


class BulkRolePermissionForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label="نقش",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    semat = forms.ModelChoiceField(
        queryset=Refrence.objects.all(),
        label="سمت",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    access_role = forms.ModelChoiceField(
        queryset=AccessRole.objects.all(),
        label="سطح دسترسی پیش‌فرض",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class PermissionFilterForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label="فیلتر بر اساس نقش",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit()'})
    )

    semat = forms.ModelChoiceField(
        queryset=Refrence.objects.all(),
        label="فیلتر بر اساس سمت",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit()'})
    )


# فرم برای ایجاد دسترسی گروهی
class MassPermissionAssignmentForm(forms.Form):
    ROLES = [(role.id, role.name) for role in Role.objects.all()]
    REFERENCES = [(ref.id, ref.name) for ref in Refrence.objects.all()]
    PERMISSIONS = [(perm.id, perm.info) for perm in Permission.objects.all()]
    ACCESS_LEVELS = [(access.id, access.name) for access in AccessRole.objects.all()]

    roles = forms.MultipleChoiceField(
        choices=ROLES,
        label="نقش‌ها",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    references = forms.MultipleChoiceField(
        choices=REFERENCES,
        label="سمت‌ها",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    permissions = forms.MultipleChoiceField(
        choices=PERMISSIONS,
        label="دسترسی‌ها",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    access_level = forms.ChoiceField(
        choices=ACCESS_LEVELS,
        label="سطح دسترسی",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
