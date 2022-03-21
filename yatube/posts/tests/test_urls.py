from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post, Follow
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)


class PostURLTests(TestCase):
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
            pk=100
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(User.objects.get(username='auth'))

    def test_post_urls_exist_anon_user(self):
        urls_templates_anon = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{PostURLTests.group.slug}/',
            'posts/profile.html': f'/profile/{PostURLTests.user.username}/',
            'posts/post_detail.html': f'/posts/{PostURLTests.post.pk}/'
        }

        for template, address in urls_templates_anon.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_urls_exist_auth_user(self):
        urls_templates_auth = {
            'posts/create_post.html': '/create/'
        }

        for template, address in urls_templates_auth.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_urls_exist_author(self):
        urls_templates_author = {
            'posts/create_post.html': f'/posts/{PostURLTests.post.pk}/edit/'
        }

        for template, address in urls_templates_author.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_auth_user_can_follow_unfollow(self):
        reverse_names = (
            reverse('posts:profile_follow',
                    kwargs={'username': PostURLTests.post.author.username}
                    ),
            reverse('posts:profile_unfollow',
                    kwargs={'username': PostURLTests.post.author.username}
                    )
        )
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                follow_count = Follow.objects.count()
                self.authorized_client.get(reverse_name)
                follow_count_new = Follow.objects.count()
                self.assertNotEqual(follow_count, follow_count_new)

    def test_user_cant_follow_himself(self):
        follow_count = Follow.objects.count()
        self.author_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostURLTests.post.author.username}
                    )
        )
        follow_count_new = Follow.objects.count()
        self.assertEqual(follow_count, follow_count_new)
