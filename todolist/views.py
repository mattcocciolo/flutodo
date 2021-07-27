from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from todolist.serializers import UserSerializer, TaskSerializer
from .models import Task


class TaskList(LoginRequiredMixin, ListView):
    """List all the tasks."""
    model = Task
    context_object_name = 'tasks'
    template_name = 'todolist/task_list.html'

    def get_context_data(self, **kwargs):
        """Restrict the task list, shows only those of the user who is logged in"""
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(is_complete=True).count()
        context['count_total'] = context['tasks'].all().count()
        try:
            context['percent'] = round((context['count'] / context['count_total']) * 100, 2)
        except ZeroDivisionError:
            context['percent'] = 0

        return context


class CreateTask(LoginRequiredMixin, CreateView):
    """Create an item in the task list."""
    model = Task
    fields = ['item_name']
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        """Create item restricted for only login user."""
        form.instance.user = self.request.user

        return super(CreateTask, self).form_valid(form)


class Login(LoginView):
    """Login of registered user."""
    template_name = 'todolist/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('task_list')


class Register(FormView):
    """New user registration"""
    template_name = 'todolist/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        """To make sure the user is logged in when press submit."""
        user = form.save()
        if user is not None:
            login(self.request, user)

        return super(Register, self).form_valid(form)

    def get(self, *args, **kwargs):
        """Restricts the ability to register, when are already logged in."""
        if self.request.user.is_authenticated:
            return redirect('task_list')

        return super(Register, self).get(*args, **kwargs)


class GetTaskObject:
    def get_task_object(self, pk):
        """Take the object from the list."""
        if self.method == "GET":
            task_item = Task.objects.get(pk=pk)
            task_item.pk = pk
            return task_item


class TaskFunction:
    """Manage check, uncheck and delete"""

    def check_complete(self, pk):
        """Check and uncheck the items of the task list."""
        task_item = GetTaskObject.get_task_object(self, pk)
        if task_item.is_complete:
            task_item.is_complete = False
            task_item.save()
        else:
            task_item.is_complete = True
            task_item.save()

        return redirect('task_list')

    def delete_task(self, pk):
        """Remove a task from the list."""
        task_item = GetTaskObject.get_task_object(self, pk)
        task_item.delete()
        messages.success(self, f'The item {task_item} has been deleted '
                               f'successfully!!!')

        return redirect('task_list')


########################################################################
"""API Rest"""


########################################################################


class UserCreate(generics.CreateAPIView):
    """Account registration via API Rest"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class LoginViewApi(APIView):
    """Login via API Rest"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)


class LogoutViewApi(APIView):
    """Logout via API Rest."""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class ItemList(ListAPIView):
    """Show the item list via API Rest."""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset


class CreateItem(CreateAPIView):
    """Add new item to the list via API Rest."""
    queryset = Task.user
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DeleteItem(DestroyAPIView):
    """Take an id and remove the associated item, remove the instance."""
    serializer_class = TaskSerializer
    lookup_field = 'pk'
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CheckUncheckComplete(UpdateAPIView):
    """Takes an id and updates the elements in our case is_complete true or false. """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'pk'
    permission_classes = (IsAuthenticated,)
