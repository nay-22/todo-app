from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    CreateTodoItemView,
    CreateUserView,
    ListAllTodoItemsView,
    ListTodoItemView,
    ListUserView,
    UpdateTodoItemView,
    DeleteTodoItemView,
    DetailTodoItemView,
)

urlpatterns = [
    # ----------------API UTILITY---------------
    path("login/", obtain_auth_token, name="login"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("todo/all/", ListAllTodoItemsView.as_view(), name="read-all-todos"),
    path("users/", ListUserView.as_view(), name="users"),
    # ----------------API UTILITY---------------
    # -------------API DELIVERABLES-------------
    path("todo/create/", CreateTodoItemView.as_view(), name="create"),
    path("todo/<int:pk>/", DetailTodoItemView.as_view(), name="read"),
    path("todo/", ListTodoItemView.as_view(), name="read-all"),
    path("todo/update/<int:pk>/", UpdateTodoItemView.as_view(), name="update"),
    path("todo/delete/<int:pk>/", DeleteTodoItemView.as_view(), name="delete"),
    # -------------API DELIVERABLES-------------
]
