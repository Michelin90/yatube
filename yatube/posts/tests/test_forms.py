from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post, Group, Comment
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import shutil
import tempfile

User = get_user_model()
NEW_TEXT_FOR_POST = 'new_text'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEXT_FOR_COMMENT = 'comment'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.group_1 = Group.objects.create(
            title='test_group_1',
            slug='test_slug_1',
            description='test_description_1',
        )
        cls.post = Post.objects.create(
            text='test_text',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_new_post_in_db(self):
        """
        При отправке валидной формы поста с картинкой
        со страницы создания поста reverse('posts:create_post')
        создаётся новая запись в базе данных.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': NEW_TEXT_FOR_POST,
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=NEW_TEXT_FOR_POST,
                group=self.group.id,
                author=self.post.author,
                image='posts/small.gif'
            ).exists()
        )

    def test_change_post_in_db(self):
        """
        При отправке валидной формы со страницы редактирования поста
        reverse('posts:post_edit', args=('post_id',))
        происходит изменение поста с post_id в базе данных.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': NEW_TEXT_FOR_POST,
            'group': self.group_1.id,
        }
        response = self.authorised_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=NEW_TEXT_FOR_POST,
                group=self.group_1.id,
                author=self.post.author,
            ).exists()
        )

    def test_comment_on_post_page(self):
        """
        Комментарий после успешной отправки авторизованным
        пользователем появляется на странице поста.
        """
        comment_count = Comment.objects.count()
        form_data = {'text': TEXT_FOR_COMMENT}
        response = self.authorised_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=TEXT_FOR_COMMENT,
                author=self.post.author,
                post=self.post
            ).exists()
        )
