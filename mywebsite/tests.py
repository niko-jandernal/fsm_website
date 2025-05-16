from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Post, Comment, DiscussionTopic, DiscussionPost, DiscussionComment, Poll, Choice, Vote, Poll_Comment, \
    Album


class UserModelTest(TestCase):
    def test_create_user(self):
        u = User.objects.create_user(username='alice', email='alice@example.com', password='pass')
        self.assertEqual(u.username, 'alice')
        self.assertTrue(u.check_password('pass'))


class PostCommentLikeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('bob', 'bob@example.com', 'pw')
        self.post = Post.objects.create(user=self.user, caption='Test', image='posts/test.jpg')
        self.client = Client()
        self.client.login(username='bob', password='pw')

    def test_like_unlike_post(self):
        url = reverse('like_post', args=[self.post.id])
        # like
        resp = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.post.likes.filter(id=self.user.id).exists())
        # unlike
        resp = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertFalse(self.post.likes.filter(id=self.user.id).exists())

    def test_comment_posting(self):
        url = reverse('post_comment', args=[self.post.id])
        resp = self.client.post(url, {'comment': 'Nice!'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.first()
        self.assertEqual(c.content, 'Nice!')
        self.assertEqual(c.post, self.post)


class DiscussionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('carol', 'carol@example.com', 'pw')
        self.topic = DiscussionTopic.objects.create(title='Style', creator=self.user)
        self.post = DiscussionPost.objects.create(topic=self.topic,
                                                  author=self.user,
                                                  content='What’s trending?')
        self.client = Client()
        self.client.login(username='carol', password='pw')

    def test_discussion_comment(self):
        url = reverse('discussion_post_comment', args=[self.post.id])
        resp = self.client.post(url, {'comment': 'Love it!'})
        self.assertEqual(resp.status_code, 302)  # redirect back to discussions
        self.assertEqual(DiscussionComment.objects.count(), 1)
        dc = DiscussionComment.objects.first()
        self.assertEqual(dc.content, 'Love it!')
        self.assertEqual(dc.post, self.post)

    def test_discussion_like(self):
        url = reverse('discussion_like_post', args=[self.post.id])
        resp = self.client.post(url)
        self.assertTrue(self.post.likes.filter(id=self.user.id).exists())
        # unlike
        resp = self.client.post(url)
        self.assertFalse(self.post.likes.filter(id=self.user.id).exists())


class PollTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('dave', 'dave@example.com', 'pw')
        self.poll = Poll.objects.create(question='Your favourite fabric?', created_by=self.user)
        self.c1 = Choice.objects.create(poll=self.poll, choice_text='Silk')
        self.c2 = Choice.objects.create(poll=self.poll, choice_text='Cotton')
        self.client = Client()
        self.client.login(username='dave', password='pw')

    def test_vote_counts_increment_synchronously(self):
        url = reverse('vote', args=[self.poll.id])
        # first vote for c1
        self.client.post(url, {'vote': self.c1.id})
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.vote_count, 1)
        # a second vote for c1 increases again
        self.client.post(url, {'vote': self.c1.id})
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.vote_count, 2)
        # ensure c2 remains untouched
        self.c2.refresh_from_db()
        self.assertEqual(self.c2.vote_count, 0)

    def test_vote_and_switch_via_ajax(self):
        """
        The AJAX view should decrement the original choice and increment the new one.
        """
        url = reverse('vote_ajax', args=[self.poll.id])
        # cast initial vote for choice 1
        resp1 = self.client.post(
            url,
            {'choice_id': self.c1.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp1.status_code, 200)
        self.c1.refresh_from_db(); self.c2.refresh_from_db()
        self.assertEqual(self.c1.vote_count, 1)
        self.assertEqual(self.c2.vote_count, 0)

        # switch vote to choice 2
        resp2 = self.client.post(
            url,
            {'choice_id': self.c2.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp2.status_code, 200)
        # after switching, c1 should be back to 0 and c2 up to 1
        self.c1.refresh_from_db(); self.c2.refresh_from_db()
        self.assertEqual(self.c1.vote_count, 0)
        self.assertEqual(self.c2.vote_count, 1)

class AlbumTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('erin', 'erin@example.com', 'pw')
        self.post = Post.objects.create(user=self.user, caption='Pic', image='posts/pic.jpg')
        self.album = Album.objects.create(owner=self.user, title='Favourites')
        self.client = Client()
        self.client.login(username='erin', password='pw')

    def test_add_and_remove_photo(self):
        add_url = reverse('add_photo', args=[self.album.id, self.post.id])
        resp = self.client.get(add_url)
        self.assertIn(self.post, self.album.posts.all())
        remove_url = reverse('remove_photo', args=[self.album.id, self.post.id])
        resp = self.client.get(remove_url)
        self.assertNotIn(self.post, self.album.posts.all())

    def test_delete_album(self):
        del_url = reverse('album_delete', args=[self.album.id])
        resp = self.client.post(del_url)
        self.assertFalse(Album.objects.filter(id=self.album.id).exists())
