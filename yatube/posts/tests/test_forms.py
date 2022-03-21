import shutil
import tempfile

from ..forms import PostForm, CommentForm
from ..models import Post, Group, Comment
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import datetime as dt
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более 15 символов',
            pk=100,
            group=cls.group,
            pub_date=dt.datetime(2022, 3, 3),
            image=uploaded
        )
        cls.form = PostForm()
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.post
        )
        cls.comment_form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(User.objects.get(username='auth'))

    def test_create_post_anon_user(self):
        """Незарегистрированный пользователь не может создать пост."""
        form_data = {
            'author': PostFormTests.post.author,
            'text': PostFormTests.post.text,
            'pk': PostFormTests.post.pk,
            'group': PostFormTests.post.group.id,
            'pub_date': PostFormTests.post.pub_date,
            'image': PostFormTests.post.image.name
        }

        response_guest = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_guest,
                             '/auth/login/?next=/create/')

    def test_create_post_auth_user(self):
        """Валидная форма создает новый пост."""
        posts_count = Post.objects.count()

        form_data = {
            'author': PostFormTests.post.author,
            'text': PostFormTests.post.text,
            'pk': PostFormTests.post.pk,
            'group': PostFormTests.post.group.id,
            'pub_date': PostFormTests.post.pub_date,
            'image': PostFormTests.post.image.name
        }

        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response,
                             reverse('posts:profile', kwargs={'username':
                                     f'{PostFormTests.post.author.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.post.author,
                text=PostFormTests.post.text,
                pk=PostFormTests.post.pk,
                group=PostFormTests.post.group,
                pub_date=PostFormTests.post.pub_date,
                image=PostFormTests.post.image.name
            ).exists()
        )

    def test_post_edit_anon_user(self):
        form_data = {
            'author': PostFormTests.post.author,
            'text': 'Новый текст',
            'pk': PostFormTests.post.pk,
            'group': PostFormTests.group.id,
            'pub_date': PostFormTests.post.pub_date,
            'image': PostFormTests.post.image.name
        }

        response_guest = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostFormTests.post.pk}'}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response_guest, f'/auth/login/?next=/posts/'
                             f'{PostFormTests.post.pk}/edit/')

    def test_post_edit_auth_user(self):
        posts_count = Post.objects.count()

        form_data = {
            'author': PostFormTests.post.author,
            'text': 'Новый текст',
            'pk': PostFormTests.post.pk,
            'group': PostFormTests.group.id,
            'pub_date': PostFormTests.post.pub_date,
            'image': PostFormTests.post.image.name
        }

        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostFormTests.post.pk}'}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': f'{PostFormTests.post.pk}'}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.post.author,
                text='Новый текст',
                pk=PostFormTests.post.pk,
                group=PostFormTests.group,
                pub_date=PostFormTests.post.pub_date,
                image=PostFormTests.post.image.name
            ).exists()
        )

    def test_comment_anon_user(self):
        form_data = {
            'author': PostFormTests.comment.author,
            'text': PostFormTests.comment.text,
            'post': PostFormTests.comment.post.id
        }
        response_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id':
                    f'{PostFormTests.comment.post.id}'}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response_guest, f'/auth/login/?next=/posts/'
                             f'{PostFormTests.comment.post.id}/comment/')

    def test_comment_auth_user(self):
        comments_count = Comment.objects.count()

        form_data = {
            'author': PostFormTests.comment.author,
            'text': PostFormTests.comment.text,
            'post': PostFormTests.comment.post.id
        }

        response = self.author_client.post(
            reverse('posts:add_comment', kwargs={'post_id':
                    f'{PostFormTests.comment.post.id}'}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id':
                                     f'{PostFormTests.comment.post.id}'}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                author=PostFormTests.comment.author,
                text=PostFormTests.comment.text,
                post=PostFormTests.comment.post.id
            ).exists()
        )
