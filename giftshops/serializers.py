from rest_framework import serializers
from giftshops.models.giftshops import AddCategory, Product

class AddCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AddCategory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create a new category."""
        return AddCategory.objects.create(**validated_data)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        """Create a new product and set created_by automatically if request user is available."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return Product.objects.create(**validated_data)
