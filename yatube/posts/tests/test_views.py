from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from posts.models import Post, Group, Follow
import shutil
import tempfile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
NUMBER_OF_POSTS_PAGINATOR = 13
NUMBER_OF_POSTS_1ST_PAGE = 10
NUMBER_OF_POSTS_2ND_PAGE = 3
NEW_TEXT_FOR_POST = 'new_text'
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostUrlsTests(TestCase):
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
            title='test_group_1',
            slug='test_slug_1',
            description='test_description_1',
        )
        cls.group_2 = Group.objects.create(
            title='test_group_2',
            slug='test_slug_2',
            description='test_description_2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_post',
            group=cls.group,
            image=cls.uploaded
        )
        cls.context_page_names = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ): 'page_obj',
            reverse(
                'posts:profile', kwargs={'username': cls.post.author}
            ): 'page_obj',
        }
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id}
            ): 'posts/post_create.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def context_assert(self, page):
        first_object = page.context['page_obj'][0]
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.id, self.post.id)
        self.assertEqual(first_object.image, self.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, template in self.templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформированы с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.context_assert(response)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформированы с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.context_assert(response)

    def test_profile_correct_context(self):
        """Шаблон profile сформированы с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author})
        )
        self.context_assert(response)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id]))
        )
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').id, self.post.id)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_post_create_post_edit_correct_context(self):
        """
        Шаблоны post_create и post_edit сформированы с правильным контекстом.
        """
        page_names = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        for name in page_names:
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                    'image': forms.fields.ImageField
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = (
                            response.context.get('form').fields.get(value)
                        )
                        self.assertIsInstance(form_field, expected)

    def test_post_with_group_in_pages(self):
        """
        При создании поста, если указать группу, то
        этот пост появится на страницах: index, group_list(выбранной группы),
        profile(профайл автора поста).
        """
        for name, context in self.context_page_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertIn(
                    self.post, response.context.get(context).object_list
                )

    def test_post_with_group_not_in_page_of_group_2(self):
        """
        Пост с указанной группой group не попал на страницу group_2.
        """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_2.slug})
        )
        self.assertNotIn(
            self.post, response.context.get('page_obj').object_list
        )


class PostPaginatorsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )

        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f'test_post {n}',
                    author=cls.user,
                    group=cls.group,
                )
                for n in range(NUMBER_OF_POSTS_PAGINATOR)
            ]
        )
        cls.page_context = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ): 'page_obj',
            reverse(
                'posts:profile', kwargs={'username': cls.user}
            ): 'page_obj',
        }

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        """
        Количество постов на первых страницах
        index, group_list, profile равно 10.
        """
        for name, context in self.page_context.items():
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(len(
                    response.context[context]), NUMBER_OF_POSTS_1ST_PAGE
                )

    def test_first_page_contains_ten_records(self):
        """
        Количество постов на вторых страницах
        index, group_list, profile равно 3.
        """
        for name, context in self.page_context.items():
            with self.subTest(name=name):
                response = self.client.get(name + '?page=2')
                self.assertEqual(len(
                    response.context[context]), NUMBER_OF_POSTS_2ND_PAGE
                )


class PostCacheTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.client = Client()
        cache.clear()

    def test_cache_index(self):
        """Контент страницы обновляется только после очистки кеша"""
        response_1 = self.client.get(reverse('posts:index'))
        Post.objects.create(
            text=NEW_TEXT_FOR_POST,
            author=self.user
        )
        response_2 = self.client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response_1.content, response_3.content)


class PostFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')
        cls.post = Post.objects.create(
            text='text',
            author=cls.author
        )
        Follow.objects.create(
            author=cls.author,
            user=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client = Client()
        self.another_user = User.objects.create_user(username='another_user')
        self.another_authorized_client.force_login(self.another_user)

    def test_create_following(self):
        """
        Авторизованный пользователь может
        подписываться на других пользователей.
        """
        following_count = Follow.objects.count()
        response = self.another_authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author})
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author})
        )
        self.assertEqual(Follow.objects.count(), following_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                author=self.author,
                user=self.another_user
            ).exists()
        )

    def test_unfollowing(self):
        """
        Авторизованный пользователь может удалять
        из своих подписок других пользователей.
        """
        following_count = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.author})
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author})
        )
        self.assertEqual(Follow.objects.count(), following_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                author=self.author,
                user=self.user
            ).exists()
        )

    def test_follow_page_new_post(self):
        """
        Новая запись пользователя появляется на странице follow
        тех, кто на него подписан.
        """
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context.get('page_obj').object_list)

    def test_follow_page_no_new_post(self):
        """
        Новая запись пользователя не появляется на странице follow
        тех, кто на него не подписан.
        """
        response = self.another_authorized_client.get(reverse(
            'posts:follow_index')
        )
        self.assertNotIn(self.post, response.context.get(
            'page_obj').object_list
        )
