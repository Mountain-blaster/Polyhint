from rest_framework import serializers
from .models import Eleve

class EleveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Eleve
        fields = '__all__'