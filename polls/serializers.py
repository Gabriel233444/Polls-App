from rest_framework import serializers
from django.conf import settings

from .models import Poll, Choice, Vote

poll=Poll
choice=Choice
vote=Vote

class PollListSerializer(serializers.ModelSerializer):
    """ Seralizer for PollSerializer """
    
    class Meta:
        fields = ['__all__']
        model = poll
        
class PollDestroySerializer(serializers.ModelSerializer):
    """ Seralizer for PollSerializer """
    
    class Meta:
        fields = ('__all__')
        model = poll
        

class PollAddSerializer(serializers.ModelSerializer):
    """ Seralizer for PollSerializer """
    
    class Meta:
        fields = ('__all__')
        model = poll
        
class PollEditSerializer(serializers.ModelSerializer):
    """ Seralizer for PollSerializer """
    
    class Meta:
        fields = ('__all__')
        model = poll
               

class ChoiceEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = choice
        
class ChoiceAddSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = choice
        
class ChoiceDestroySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = choice
        
class ChoiceRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = choice
        
class VoteListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = vote
        
        
class VoteEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = vote
        
class VoteDestroySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = vote