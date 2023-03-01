from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, UpdateAPIView, CreateAPIView, ListCreateAPIView, DestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser  
from rest_framework import status

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages

from .models import Poll, Choice, Vote
from .serializers import PollListSerializer, PollDestroySerializer, PollAddSerializer, PollEditSerializer, ChoiceEditSerializer, ChoiceAddSerializer, VoteSerializer
from .forms import PollAddForm, EditPollForm, ChoiceAddForm
from django.http import HttpResponse

poll_model = Poll
choice_model = Choice

class PollsListViewSet(ListAPIView):
    queryset = poll_model.objects.all()
    serializer_class = PollListSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(poll_model.objects.filter(renter=id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class PollsCreatViewSet(CreateAPIView):
    queryset = poll_model.objects.all()
    serializer_class = PollAddSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
    

class PollsEditViewSet(RetrieveUpdateAPIView):
    queryset = poll_model.objects.all()
    serializer_class = PollEditSerializer
    

class PollsDeleteViewSet(DestroyAPIView):
    queryset = poll_model.objects.all()
    serializer_class = PollDestroySerializer
    

class ChoiceAddViewSet(CreateAPIView):
    queryset = choice_model.objects.all()
    serializer_class = ChoiceAddSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class ChoiceEditViewSet(RetrieveUpdateAPIView):
    queryset = choice_model.objects.all()
    serializer_class = ChoiceEditSerializer


@login_required
def choice_delete(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('home')
    choice.delete()
    messages.success(
        request, "Choice Deleted successfully.", extra_tags='alert alert-success alert-dismissible fade show')
    return redirect('polls:edit', poll.id)


def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.active:
        return render(request, 'polls/poll_result.html', {'poll': poll})
    loop_count = poll.choice_set.count()
    context = {
        'poll': poll,
        'loop_time': range(0, loop_count),
    }
    return render(request, 'polls/poll_detail.html', context)


@login_required
def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choice_id = request.POST.get('choice')
    if not poll.user_can_vote(request.user):
        messages.error(
            request, "You already voted this poll!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("polls:list")

    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        vote = Vote(user=request.user, poll=poll, choice=choice)
        vote.save()
        print(vote)
        return render(request, 'polls/poll_result.html', {'poll': poll})
    else:
        messages.error(
            request, "No choice selected!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("polls:detail", poll_id)
    return render(request, 'polls/poll_result.html', {'poll': poll})


@login_required
def endpoll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if poll.active is True:
        poll.active = False
        poll.save()
        return render(request, 'polls/poll_result.html', {'poll': poll})
    else:
        return render(request, 'polls/poll_result.html', {'poll': poll})
