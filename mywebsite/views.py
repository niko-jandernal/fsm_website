import os
import random

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import AlbumForm
from .forms import CreateUserForm
from .forms import DiscussionPostForm
from .forms import DiscussionTopicForm
from .forms import PostForm
from .models import Album, Poll_Comment
from .models import Comment
from .models import DiscussionComment
from .models import DiscussionPost
from .models import DiscussionTopic, TopicFollow
from .models import Poll, Choice
from .models import Post, Vote
from .forms import PollForm, PollCommentForm, ChoiceFormSet
from django.db.models import Sum, Count

api_key = settings.NYT_API_KEY


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        form = CreateUserForm()

        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Account was created for " + form.cleaned_data.get("username"))

                return redirect("login")
            else:
                messages.error(request, "An error occurred while creating the account, please try again.")
        else:
            form = CreateUserForm()
        context = {'form': form}
        return render(request, "register.html", context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Username or password is incorrect, please try again.")

        context = {}
        return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def home(request):
    posts = Post.objects.all().order_by('-date_posted')  # Get posts ordered by date

    for post in posts:
        post.is_liked = post.likes.filter(id=request.user.id).exists()
        post.comments_list = post.comments.all().order_by('-date_posted')  # Newest comments first
        post.has_more_comments = post.comments.count() > 2
        post.total_comments = post.comments.count()
    return render(request, 'home.html', {'posts': posts})


@login_required(login_url="login")
def like_post(request, post_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post = get_object_or_404(Post, id=post_id)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            is_liked = False

        else:
            post.likes.add(request.user)
            is_liked = True
        return JsonResponse({"total_likes": post.likes.count(), "is_liked": is_liked})

    else:
        return JsonResponse({"error": "There was an error, please try again."}, status=400)


@login_required(login_url="login")
def post_comment(request, post_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('comment')
        if content:
            comment = Comment.objects.create(post=post, author=request.user, content=content)

            return JsonResponse({"comment": content, "author": request.user.username,
                                 "date_posted": comment.date_posted.strftime('%Y-%m-%d %H:%M')})

        else:
            return JsonResponse({"error": "Comment content is empty"}, status=400)
    else:
        return JsonResponse({"error": "There was an error, please try again."}, status=400)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'home.html', {'post': post})


def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).order_by('-date_joined')
    else:
        users = User.objects.none()
    return render(request, 'search_results.html', {'users': users})


@login_required(login_url="login")
def explore(request):
    folder_path = os.path.join(settings.MEDIA_ROOT, 'images')
    images = [os.path.join(settings.MEDIA_URL, 'images', img) for img in os.listdir(folder_path)]
    random.shuffle(images)

    return render(request, 'explore.html', {'images': images})


@login_required(login_url="login")
def boards(request):
    return render(request, "boards.html")


def fetch_news(api_key):
    url = 'https://api.nytimes.com/svc/topstories/v2/fashion.json'
    params = {'api-key': api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['results']


def news(request):
    api_key = 'bLRhFHvkMwMN5npLhFdYbyPPGn1l1KdA'
    try:
        news_items = fetch_news(api_key)
        context = {'news_items': news_items}
    except requests.HTTPError as e:
        context = {'error': 'Failed to fetch news: {}'.format(e)}
    return render(request, 'news.html', context)


@login_required(login_url="login")
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'create.html', {'form': form})



@login_required(login_url="login")
def discussions(request):
    # ————————————
    # (1) Basic search & filter
    q = request.GET.get('q', '').strip()
    topic_id = request.GET.get('topic')
    posts = DiscussionPost.objects.all()

    if q:
        posts = posts.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q)
        )
    if topic_id:
        posts = posts.filter(topic__id=topic_id)

    # ————————————
    # (2) “Following” toggle
    follow_mode = (request.GET.get('following') == '1')

    # load EVERY topic for dropdown
    topics = DiscussionTopic.objects.order_by('title')

    if follow_mode:
        # fetch the TopicFollow rows for this user
        follows = TopicFollow.objects.filter(user=request.user)
        # pull out the topic-IDs they follow
        followed_topic_ids = follows.values_list('topic_id', flat=True)
        # now only show those topics
        followed_topics = topics.filter(id__in=followed_topic_ids)
        # and only show posts in those topics
        posts = posts.filter(topic__id__in=followed_topic_ids)
    else:
        followed_topics = None

    # ————————————
    # (3) Pagination
    posts = posts.order_by('-date_posted')
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ————————————
    # (4) New-post form only in “all” mode
    form = DiscussionPostForm()
    if not follow_mode and request.method == "POST":
        form = DiscussionPostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.topic_id = request.POST['topic']
            new_post.save()
            return redirect('discussions')

    # ————————————
    return render(request, 'discussions/discussions.html', {
        'q': q,
        'topic_id': topic_id,
        'topics': topics,
        'follow_mode': follow_mode,
        'followed_topics': followed_topics,
        'page_obj': page_obj,
        'form': form,
    })


@login_required(login_url="login")
def topic_follow(request, topic_id):
    topic = get_object_or_404(DiscussionTopic, id=topic_id)
    # toggle
    follow, created = TopicFollow.objects.get_or_create(
        user=request.user,
        topic=topic
    )
    if not created:
        follow.delete()
    # send them back to wherever they came from
    return redirect(request.META.get('HTTP_REFERER', 'discussions'))


@login_required(login_url="login")
def discussion_detail(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    comments = post.comments.order_by('date_posted')
    is_liked = post.likes.filter(id=request.user.id).exists()

    return render(request, 'discussions/discussion_detail.html', {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
    })


@login_required(login_url="login")
def discussion_post_comment(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('comment')
        if content:
            DiscussionComment.objects.create(post=post, author=request.user, content=content)
    return redirect('discussion_detail', post_id=post.id)


@login_required(login_url="login")
def discussion_like_post(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('discussions')


@login_required
def topic_list(request):
    q = request.GET.get('q', '').strip()
    topics = DiscussionTopic.objects.all()
    if q:
        topics = topics.filter(title__icontains=q)
    topics = topics.order_by('-created_at')
    # allow creation inline
    if request.method == 'POST':
        form = DiscussionTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.creator = request.user
            topic.save()
            return redirect('topic_list')
    else:
        form = DiscussionTopicForm()
    return render(request, 'discussions/topic_list.html', {
        'topics': topics, 'q': q, 'form': form
    })


@login_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(DiscussionTopic, id=topic_id)
    posts = topic.posts.order_by('-date_posted')
    is_following = TopicFollow.objects.filter(topic=topic, user=request.user).exists()
    return render(request, 'discussions/topic_detail.html', {
        'topic': topic, 'posts': posts, 'is_following': is_following
    })


@login_required
def topic_follow(request, topic_id):
    topic = get_object_or_404(DiscussionTopic, id=topic_id)
    follow, created = TopicFollow.objects.get_or_create(topic=topic, user=request.user)
    if not created:
        # already followed → unfollow
        follow.delete()
    return redirect('topic_detail', topic_id=topic.id)


@login_required
def following_posts(request):
    # all posts in topics this user follows
    followed = DiscussionTopic.objects.filter(followers__user=request.user)
    posts = DiscussionPost.objects.filter(topic__in=followed).order_by('-date_posted')
    return render(request, 'discussions/following.html', {
        'posts': posts
    })


@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        formset = ChoiceFormSet(request.POST, prefix='choices')
        if form.is_valid() and formset.is_valid():
            poll = form.save(commit=False)
            poll.created_by = request.user
            poll.save()
            formset.instance = poll
            formset.save()
            return redirect('poll_detail', poll_id=poll.id)
    else:
        form = PollForm()
        formset = ChoiceFormSet(prefix='choices')

    return render(request, 'polls/create_poll.html', {
        'form': form,
        'formset': formset,
    })


def view_polls(request):
    q = request.GET.get('q', '').strip()
    polls = Poll.objects.all()
    if q:
        polls = polls.filter(Q(question__icontains=q))
    polls = polls.annotate(
        total_votes=Sum('choices__vote_count'),
        comment_count=Count('comments')
    ).order_by('-created_at')

    paginator = Paginator(polls, 6)     # six cards per “page”
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'polls/view_polls.html', {
        'polls_page': page_obj,
        'q': q,
    })


@login_required(login_url="login")
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = poll.choices.get(pk=request.POST['vote'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/view_polls.html', {
            'poll': poll,
            'error_message': "You didn't select a choice or an invalid choice was made.",
        })
    else:
        selected_choice.vote_count += 1
        selected_choice.save()

        return redirect('view_polls')


@login_required(login_url="login")
def add_comment(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.method == 'POST':
        form = PollCommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.poll = poll
            new_comment.created_by = request.user
            new_comment.save()
            return redirect('view_polls')
        else:
            return render(request, 'home.html', {'form': form, 'poll': poll})
    else:
        form = PollCommentForm()
        return render(request, 'polls/view_polls.html', {'form': form, 'poll': poll})


@login_required(login_url="login")
@require_POST
def comment_ajax(request, poll_id):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    poll = get_object_or_404(Poll, pk=poll_id)
    content = request.POST.get('comment_text', '').strip()
    if not content:
        return JsonResponse({'error': 'Empty comment'}, status=400)

    comment = Poll_Comment.objects.create(
        poll=poll,
        comment_text=content,
        created_by=request.user
    )

    # Return the new comment’s data for immediate rendering
    return JsonResponse({
        'comment_text': comment.comment_text,
        'author': comment.created_by.username,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
    })


@login_required(login_url="login")
def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choices = list(poll.choices.all())
    counts = [c.vote_count for c in choices]
    total = sum(counts) or 1

    # Get user's current vote
    try:
        user_vote = Vote.objects.get(poll=poll, voted_by=request.user)
        user_choice_id = user_vote.choice.id
    except Vote.DoesNotExist:
        user_choice_id = None

    data = []
    for choice, count in zip(choices, counts):
        pct = round(count * 100 / total, 1)
        data.append({
            'id': choice.id,
            'text': choice.choice_text,
            'count': count,
            'pct': pct,
        })

    comments = poll.comments.all().order_by('-created_at')

    return render(request, 'polls/detail.html', {
        'poll': poll,
        'chart_data': data,
        'total_votes': total,
        'comments': comments,
        'user_choice_id': user_choice_id,
    })

@login_required(login_url="login")
@require_POST
def vote_ajax(request, poll_id):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    poll = get_object_or_404(Poll, pk=poll_id)
    choice_id = request.POST.get('choice_id')

    try:
        new_choice = poll.choices.get(pk=choice_id)
    except (KeyError, Choice.DoesNotExist):
        return JsonResponse({'error': 'Choice not found'}, status=404)

    # Check for existing vote and update if needed
    try:
        vote = Vote.objects.get(poll=poll, voted_by=request.user)
        old_choice = vote.choice
        if old_choice != new_choice:
            # Decrement old choice count
            old_choice.vote_count = max(0, old_choice.vote_count - 1)
            old_choice.save()
            # Update vote to new choice
            vote.choice = new_choice
            vote.save()
            # Increment new choice count
            new_choice.vote_count += 1
            new_choice.save()
    except Vote.DoesNotExist:
        # Create new vote
        Vote.objects.create(poll=poll, choice=new_choice, voted_by=request.user)
        new_choice.vote_count += 1
        new_choice.save()

    # Return updated data
    labels = [c.choice_text for c in poll.choices.all()]
    counts = [c.vote_count for c in poll.choices.all()]

    return JsonResponse({'labels': labels, 'counts': counts})


@login_required
def album_list(request):
    # 1) Show all albums owned by you
    albums = request.user.albums.all().order_by('-created_at')
    return render(request, 'albums/list.html', {'albums': albums})


@login_required
def album_create(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = request.user
            album.save()
            return redirect('album_detail', album.id)
    else:
        form = AlbumForm()
    return render(request, 'albums/form.html', {'form': form})


@login_required
def album_detail(request, album_id):
    # only let the owner view their own album
    album = get_object_or_404(Album, id=album_id, owner=request.user)

    # photos already added
    album_posts = album.posts.all().order_by('-date_posted')

    # your uploads _not_ yet in this album
    your_photos = (
        Post.objects
        .filter(user=request.user)
        .exclude(id__in=album_posts.values_list('id', flat=True))
        .order_by('-date_posted')
    )

    # other users' uploads _not_ yet in this album
    all_other_photos = (
        Post.objects
        .exclude(user=request.user)
        .exclude(id__in=album_posts.values_list('id', flat=True))
        .order_by('-date_posted')
    )

    return render(request, 'albums/detail.html', {
        'album': album,
        'album_posts': album_posts,
        'your_photos': your_photos,
        'all_other_photos': all_other_photos,
    })


@login_required(login_url="login")
def album_add_photo(request, album_id, post_id):
    # only owner can add
    album = get_object_or_404(Album, id=album_id, owner=request.user)
    post = get_object_or_404(Post, id=post_id)
    album.posts.add(post)
    return redirect('album_detail', album.id)


@login_required(login_url="login")
def album_remove_post(request, album_id, post_id):
    # get the album and make sure it belongs to the current user
    album = get_object_or_404(Album, id=album_id, owner=request.user)
    # get the post to remove
    post = get_object_or_404(Post, id=post_id)
    # remove it from the album’s M2M
    album.posts.remove(post)
    # send you back to the album detail page
    return redirect('album_detail', album_id=album.id)


@login_required
def album_delete(request, album_id):
    alb = get_object_or_404(Album, id=album_id, owner=request.user)
    if request.method == 'POST':
        alb.delete()
        return redirect('album_list')
    # if GET, show a simple confirmation page
    return render(request, 'albums/confirm_delete.html', {'album': alb})
