from rest_framework import serializers

from .models import Poll, Choice, Vote

poll=Poll
choice=Choice
vote=Vote

class PollListSerializer(serializers.ModelSerializer):
    """ Seralizer for PollSerializer """
    
    class Meta:
        fields = ('__all__')
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
        
class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = vote