from rest_framework import serializers
from rest_framework.reverse import reverse
from tbnr.models import CustomUser, Image, Plan, ExpiringLink


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username','password')


class AddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['name', 'file']
        read_only_fields = ['uploaded_by']


class ListSerializer(serializers.ModelSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='details', lookup_field='pk')

    class Meta:
        model = Image
        fields = ['name', 'details', 'uploaded_by']


class ImageSerializer(serializers.ModelSerializer):
    plan_name = serializers.SerializerMethodField()
    plan_heights = serializers.SerializerMethodField()


    class Meta:
        model = Image
        fields = ['id', 'name', 'height', 'width', 'plan_name', 'plan_heights']

    def get_plan_name(self, obj):
        if obj.uploaded_by and obj.uploaded_by.plan:
            return obj.uploaded_by.plan.name
        return None

    def get_plan_heights(self, obj):
        if obj.uploaded_by and obj.uploaded_by.plan:
            request = self.context.get('request')
            sizes = []

            for height in obj.uploaded_by.plan.height.all():
                url = reverse('thumbnail', args=[str(height), str(obj.id)], request=request)
                sizes.append({'size': height.size, 'url': url})
            return sizes
        return []



class ExpiringLinkSerializer(serializers.ModelSerializer):
    expiration_time = serializers.IntegerField(min_value=300, max_value=30000)

    class Meta:
        model = ExpiringLink
        fields = ['image', 'expiration_time']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            fields['image'].queryset = user.image_set.all()
        return fields