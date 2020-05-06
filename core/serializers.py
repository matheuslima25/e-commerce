from rest_framework import serializers
from core import models


class ProdutosSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField('get_image_url')

    class Meta:
        fields = '__all__'
        model = models.Produto

    def get_image_url(self, obj):
        return obj.image.url