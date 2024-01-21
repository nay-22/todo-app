from rest_framework.test import APIClient

from rest_framework import status
from django.test import TestCase

from .models import Tag, TodoItem, User
from .utils import validate_due_date
from .serializers import UserSerializer, UserRegisterSerializer, TodoItemSerializer

from datetime import date, timedelta


# ---------------------- UTILS TESTCASE ----------------------
class UtilsTest(TestCase):
    def setUp(self):
        self.valid_due_date = str(date.today().strftime("%Y-%m-%d"))
        self.invalid_due_date = str(
            (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        )

    def test_util_date_validator(self):
        self.assertEqual(validate_due_date(self.invalid_due_date), self.valid_due_date)


# ------------------------------------------------------------


# ---------------------- MODEL TESTCASE ----------------------
class TagModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(title="tag1")

    def test_tag_creation(self):
        self.assertEqual(str(self.tag), "tag1")


class TodoItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")

        self.todo = TodoItem.objects.create(
            title="Buy Groceries",
            description="Milk, Almonds, Oranges, Bread",
            due_date=str(date.today()),
            user=self.user,
            status="OPEN",
        )

        self.tag1 = Tag.objects.create(title="tag1")
        self.tag2 = Tag.objects.create(title="tag2")

        self.todo.tags.add(self.tag1)
        self.todo.tags.add(self.tag2)

    def test_todo_item_creation(self):
        self.assertEqual(str(self.todo), "Buy Groceries")


# ------------------------------------------------------------


# -------------------- SERIALIZER TESTCASE -------------------
class UserRegisterSerializerTest(TestCase):
    def setUp(self):
        self.request_data = {"username": "testuser", "password": "testpassword"}

    def test_user_register_serializer(self):
        serializer = UserRegisterSerializer(data=self.request_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(user.check_password("testpassword"))


class TodoItemSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")
        self.tag1 = Tag.objects.create(title="Tag1")
        self.tag2 = Tag.objects.create(title="Tag2")
        self.todo_item = TodoItem.objects.create(
            title="Test Todo",
            timestamp="2024-01-20T16:26:41.630134Z",
            description="Test description",
            due_date="2024-01-22",
            user=self.user,
            status="OPEN",
        )
        self.todo_item.tags.add(self.tag1, self.tag2)

    def test_todo_item_serializer_to_representation(self):
        serializer = TodoItemSerializer(instance=self.todo_item)
        serialized_data = serializer.data.copy()
        serialized_data.pop("timestamp", None)
        expected_representation = {
            "id": self.todo_item.id,
            "tags": ["Tag1", "Tag2"],
            "title": "Test Todo",
            "description": "Test description",
            "due_date": "2024-01-22",
            "status": "OPEN",
            "user": self.user.id,
        }
        self.assertEqual(serialized_data, expected_representation)


# ------------------------------------------------------------


# ---------------------- VIEW TESTCASE -----------------------
class CreateUserViewTest(TestCase):
    def setUp(self):
        self.request_data = {"username": "testuser", "password": "testpassword"}
        self.expected_data = {
            "username": "testuser",
            "password": "pbkdf2_sha256$600000$LZadOrrlvFp407RjOXYnR9$0a6A0a97VJTgYL3B24EWCI167vbkb4XfZyLUYZbXI2k=",
        }
        self.client = APIClient()

    def test_create_user_view(self):
        url = "/api/register/"
        response = self.client.post(url, self.request_data, format="json")
        expected_data = {
            "username": "testuser",
            "password": response.json()["password"],
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), expected_data)


class ListAllTodoItemsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")

        self.expected_data = [
            {
                "id": 1,
                "tags": ["tag1", "tag2"],
                "title": "Test Item 1",
                "description": "Test Item 1 Description",
                "due_date": "2024-01-20",
                "status": "OPEN",
                "user": 1,
            },
            {
                "id": 2,
                "tags": ["tag1", "tag2"],
                "title": "Test Item 1",
                "description": "Test Item 1 Description",
                "due_date": "2024-01-20",
                "status": "OPEN",
                "user": 1,
            },
        ]

        self.client = APIClient()

        self.tag1 = Tag.objects.create(title="tag1")
        self.tag2 = Tag.objects.create(title="tag2")

        self.todo_item1 = TodoItem.objects.create(
            title="Test Item 1",
            timestamp="2024-01-20T16:26:41.630134Z",
            description="Test Item 1 Description",
            due_date="2024-01-20",
            user=self.user,
            status="OPEN",
        )
        self.todo_item1.tags.add(self.tag1, self.tag2)

        self.todo_item2 = TodoItem.objects.create(
            title="Test Item 1",
            timestamp="2024-01-20T16:26:41.630134Z",
            description="Test Item 1 Description",
            due_date="2024-01-20",
            user=self.user,
            status="OPEN",
        )
        self.todo_item2.tags.add(self.tag1, self.tag2)

    def test_list_all_todo_items(self):
        url = "/api/todo/all/"
        response = self.client.get(url, format="json")

        json_data = response.json()
        for data in json_data:
            data.pop("timestamp")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.expected_data)


class ListUserViewTest(TestCase):
    def setUp(self):
        self.luffy = User.objects.create_user(username="luffy", password="password")
        self.zoro = User.objects.create_user(username="zoro", password="password")

        self.client = APIClient()

    def test_list_user_view(self):
        url = "/api/users/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = UserSerializer(User.objects.all(), many=True).data
        self.assertEqual(response.json(), expected_data)


class CreateTodoItemViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_todo_item_view_201(self):
        request = {
            "user": self.user.id,
            "title": "Test Todo",
            "description": "Test Todo Description",
            "due_date": "2024-01-28",
            "status": "OPEN",
            "tags": ["tag2", "tag1"],
        }
        url = "/api/todo/create/"
        response = self.client.post(url, request, format="json")
        deserialized = TodoItemSerializer(
            TodoItem.objects.get(id=response.json()["id"])
        ).data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), deserialized)

    def test_create_todo_item_view_400_date(self):
        request = {
            "user": self.user.id,
            "title": "Test Todo",
            "description": "Test Todo Description",
            "due_date": "28-01-2024",
            "status": "OPEN",
            "tags": ["tag2", "tag1"],
        }
        url = "/api/todo/create/"
        response = self.client.post(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "error": f"time data '{request['due_date']}' does not match format '%Y-%m-%d'"
            },
        )

    def test_create_todo_item_view_400_serializer_invalid(self):
        request = {
            "title": "Test Todo",
            "description": "Test Todo Description",
            "due_date": "2024-01-28",
            "status": "SOMETHING",  # 400, Bad Request
            "tags": ["tag1", "tag2"],
        }
        url = "/api/todo/create/"
        response = self.client.post(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"status": ['"SOMETHING" is not a valid choice.']}
        )


class DetailTodoItemViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.todo = TodoItem.objects.create(
            title="Test Todo",
            description="Test Todo Description",
            due_date="2024-01-23",
            status="WORKING",
            user=self.user,
        )

        self.tag1 = Tag.objects.create(title="tag1")
        self.tag2 = Tag.objects.create(title="tag2")

        self.todo.tags.add(self.tag1, self.tag2)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_detail_todo_view(self):
        url = "/api/todo/1/"
        response = self.client.get(url, format="json")
        serializer = TodoItemSerializer(TodoItem.objects.get(id=1)).data
        self.assertEqual(response.json(), serializer)

    def test_detail_todo_view_404(self):
        url = "/api/todo/2/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json(), {"error": "TodoItem matching query does not exist."}
        )


class ListTodoItemViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.tag1 = Tag.objects.create(title="tag1")
        self.tag2 = Tag.objects.create(title="tag2")

        self.todo1 = TodoItem.objects.create(
            title="Test Todo 1",
            description="Test Todo 1 Description",
            due_date="2024-01-23",
            status="WORKING",
            user=self.user,
        )
        self.todo1.tags.add(self.tag1, self.tag2)

        self.todo2 = TodoItem.objects.create(
            title="Test Todo 2",
            description="Test Todo 2 Description",
            due_date="2024-01-29",
            status="OPEN",
            user=self.user,
        )
        self.todo2.tags.add(self.tag1, self.tag2)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_todo_view(self):
        url = "/api/todo/"
        response = self.client.get(url, format="json")
        serializer = TodoItemSerializer(TodoItem.objects.all(), many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serializer.data)


class UpdateTodoItemViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.tag1 = Tag.objects.create(title="tag1")
        self.tag2 = Tag.objects.create(title="tag2")

        self.todo = TodoItem.objects.create(
            title="Test Todo",
            description="Test Todo Description",
            due_date="2024-01-23",
            status="WORKING",
            user=self.user,
        )
        self.todo.tags.add(self.tag1, self.tag2)

        self.request = {
            "title": "Updated Test Todo",
            "description": "Updated Test Todo Description",
            "status": "DONE",
            "tags": ["tag3", "tag4"],
        }

        self.request_wrong_date = {
            "title": "Updated Test Todo",
            "description": "Updated Test Todo Description",
            "status": "DONE",
            "due_date": str(date.today().strftime("%d-%m-%Y")),
            "tags": ["tag3", "tag4"],
        }

        self.request_invalid_serializer = {
            "title": "Updated Test Todo",
            "description": "Updated Test Todo Description",
            "due_date": "2024-01-28",
            "status": "SOMETHING",  # 400, Bad Request
            "tags": ["tag1", "tag2"],
        }

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_update_todo_item_view(self):
        url = "/api/todo/update/1/"
        response = self.client.put(url, self.request, format="json")
        serializer = TodoItemSerializer(TodoItem.objects.get(id=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serializer.data)

    def test_update_todo_item_view_404(self):
        url = "/api/todo/update/2/"
        response = self.client.put(url, self.request, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json(), {"error": "TodoItem matching query does not exist."}
        )

    def test_update_todo_item_view_400_date(self):
        url = "/api/todo/update/1/"
        response = self.client.put(url, self.request_wrong_date, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "error": f"time data '{self.request_wrong_date['due_date']}' does not match format '%Y-%m-%d'"
            },
        )

    def test_update_todo_item_view_400_invalid_serializer(self):
        url = "/api/todo/update/1/"
        response = self.client.put(url, self.request_invalid_serializer, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"status": ['"SOMETHING" is not a valid choice.']}
        )


class DeleteTodoItemViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.tag1 = Tag.objects.create(title="tag1")
        self.tag2 = Tag.objects.create(title="tag2")

        self.todo = TodoItem.objects.create(
            title="Test Todo",
            description="Test Todo Description",
            due_date="2024-01-23",
            status="WORKING",
            user=self.user,
        )
        self.todo.tags.add(self.tag1, self.tag2)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_delete_todo_item_view(self):
        url = "/api/todo/delete/1/"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "Item 1 deleted successfully!"})

    def test_delete_todo_item_view_404(self):
        url = "/api/todo/delete/2/"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json(), {"error": "TodoItem matching query does not exist."}
        )


# -------------------------------------------------------------
