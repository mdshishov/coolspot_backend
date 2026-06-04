from django import forms

from orders.models import OrderDish


class OrderDishForm(forms.ModelForm):
    class Meta:
        model = OrderDish
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk is None:
            self.fields["dish_title"].disabled = True
            self.fields["dish_price"].disabled = True
