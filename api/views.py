from rest_framework import permissions, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist

from .serializers import TodoItemSerializer, UserRegisterSerializer, UserSerializer
from .models import TodoItem, User
from .utils import validate_due_date, get_instance_with_tags


# ----------------API UTILITY---------------
class CreateUserView(APIView):
    def post(self, request):
        user_serializer = UserRegisterSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user_serializer.save()
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


class ListAllTodoItemsView(APIView):
    def get(self, request):
        todo_serializer = TodoItemSerializer(TodoItem.objects.all(), many=True)
        return Response(todo_serializer.data, status=status.HTTP_200_OK)


class ListUserView(APIView):
    def get(self, request):
        user_serializer = UserSerializer(User.objects.all(), many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


# ----------------API UTILITY---------------


# -------------API DELIVERABLES-------------
class CreateTodoItemView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if "due_date" in request.data:
            try:
                request.data["due_date"] = validate_due_date(
                    request.data.get("due_date")
                )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        tags = request.data.pop("tags", [])
        request.data["user"] = self.request.user.pk
        todo_serializer = TodoItemSerializer(data=request.data)
        if todo_serializer.is_valid():
            todo_serializer.save()
            todo_instance = TodoItem.objects.get(id=todo_serializer.data["id"])
            # for tag in tags:
            #     tag, _ = Tag.objects.get_or_create(title=tag)
            #     todo_instance.tags.add(tag)
            # deserialized = TodoItemSerializer(todo_instance).data
            deserialized = TodoItemSerializer(
                get_instance_with_tags(todo_instance, tags)
            ).data
            return Response(deserialized, status=status.HTTP_201_CREATED)
        else:
            return Response(todo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailTodoItemView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            todo_serializer = TodoItemSerializer(
                TodoItem.objects.get(id=pk, user=self.request.user)
            )
            return Response(todo_serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


class ListTodoItemView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        todo_serializer = TodoItemSerializer(
            TodoItem.objects.filter(user=self.request.user), many=True
        )
        return Response(todo_serializer.data, status=status.HTTP_200_OK)


class UpdateTodoItemView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        try:
            if "due_date" in request.data:
                try:
                    request.data["due_date"] = validate_due_date(
                        request.data.get("due_date")
                    )
                except Exception as e:
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            todo_instance = TodoItem.objects.get(id=pk, user=self.request.user)
            tags = request.data.pop("tags", [])
            todo_instance.tags.clear()
            todo_serializer = TodoItemSerializer(
                instance=todo_instance, data=request.data
            )
            if todo_serializer.is_valid():
                todo_serializer.save()
                # prevv
                deserialized = TodoItemSerializer(
                    get_instance_with_tags(todo_instance, tags)
                ).data
                return Response(deserialized, status=status.HTTP_200_OK)
            return Response(todo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


class DeleteTodoItemView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            todo_instance = TodoItem.objects.get(id=pk, user=self.request.user)
            todo_instance.delete()
            return Response({"message": f"Item {pk} deleted successfully!"})
        except ObjectDoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


# class TagView(APIView):
#     pass


# class TagDetailView(APIView):
#     pass
