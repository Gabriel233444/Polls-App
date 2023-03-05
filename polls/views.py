from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, UpdateAPIView, CreateAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from rest_framework import status

from .models import Poll, Choice, Vote
from .serializers import PollListSerializer, PollDestroySerializer, PollAddSerializer, PollEditSerializer,\
    ChoiceEditSerializer, ChoiceAddSerializer, ChoiceDestroySerializer, ChoiceRetrieveSerializer, VoteListSerializer, \
    VoteEditSerializer, VoteDestroySerializer
from .permission import permission_required

from accounts.permission import IdentityIsVerified

poll_model = Poll
choice_model = Choice
vote_model = Vote

class NoPaginationView(PageNumberPagination):
    page_size = None
    

class PollsListViewSet(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = poll_model.objects.all()
    serializer_class = PollListSerializer
    pagination_class = NoPaginationView
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(poll_model.objects.filter())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class PollsCreatViewSet(ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = poll_model.objects.all()
    serializer_class = PollAddSerializer
    pagination_class = NoPaginationView
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
    

class PollsEditViewSet(RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = poll_model.objects.all()
    serializer_class = PollEditSerializer
    pagination_class = NoPaginationView
    

class PollsDeleteViewSet(RetrieveDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = poll_model.objects.all()
    serializer_class = PollDestroySerializer
    pagination_class = NoPaginationView
    

class ChoiceAddViewSet(ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = choice_model.objects.all()
    serializer_class = ChoiceAddSerializer
    pagination_class = NoPaginationView
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class ChoiceEditViewSet(RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = choice_model.objects.all()
    serializer_class = ChoiceEditSerializer
    pagination_class = NoPaginationView


class ChoiceDestroyViewSet(RetrieveDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = choice_model.objects.all()
    serializer_class = ChoiceDestroySerializer
    pagination_class = NoPaginationView


class ChoiceRetrieveViewSet(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = choice_model.objects.all()
    serializer_class = ChoiceRetrieveSerializer
    pagination_class = NoPaginationView
    

class VoteAddViewSet(ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = vote_model.objects.all()
    serializer_class = VoteListSerializer
    pagination_class = NoPaginationView
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class VoteEditViewSet(RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = vote_model.objects.all()
    serializer_class = VoteEditSerializer
    pagination_class = NoPaginationView
    
    
class VoteDestroyViewSet(RetrieveDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = ()
    queryset = vote_model.objects.all()
    serializer_class = VoteDestroySerializer
    pagination_class = NoPaginationView
        