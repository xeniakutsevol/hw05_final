from django.test import TestCase
from ..models import Group, Post, User

STRING_LEN = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(str(post),
                         'Тестовый пост более 15 символов'[:STRING_LEN])
        group = PostModelTest.group
        self.assertEqual(str(group), 'Тестовая группа')
