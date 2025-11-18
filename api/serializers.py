from rest_framework import serializers
from base.models import Area, GsModel, Owner, FailureSub
from accounts.models import Captcha
from sell.models import SellModel, Waybill


class AreaSerializer(serializers.ModelSerializer):
    zone = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Area
        fields = '__all__'


class FailureSerializer(serializers.ModelSerializer):
    failurecategory = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = FailureSub
        fields = '__all__'



class GSSerializer(serializers.ModelSerializer):
    area = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GsModel
        fields = '__all__'


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = '__all__'


class CaptchaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Captcha
        fields = ('id', 'img')


class SellSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellModel
        fields = '__all__'


class WaybillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waybill
        fields = '__all__'
        extra_kwargs = {
            'gsid': {'required': True},
            'waybill_id': {'required': True},
            'product_id': {'required': True},
            'quantity': {'required': True},
            'quantity60': {'required': True},
            'weight': {'required': True},
            'degree': {'required': True},
            'special_weight': {'required': True},
            'customer_name': {'required': True},
            'exit_date': {'required': True},
            'exit_time': {'required': True},
            'full_plak_with_seri': {'required': False},
            'contract_code_car': {'required': False},
            'customer_code': {'required': True},
            'car_driving_name': {'required': False},
            'car_driving_mobail': {'required': False},
            'send_type': {'required': True},
            'sender': {'required': True},
            'target': {'required': True},

        }