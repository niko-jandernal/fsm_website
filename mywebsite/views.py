from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .forms import CreateUserForm
from .forms import PostForm
from .forms import DiscussionPostForm
from .models import Comment
from .models import Post, Poll, Vote
from .models import DiscussionPost
from .models import DiscussionComment
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Poll, Choice, Poll_Comment
from .forms import PollForm, PollCommentForm


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
    return render(request, "explore.html")


@login_required(login_url="login")
def boards(request):
    return render(request, "boards.html")


def news(request):
    return render(request, "news.html")


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
    if request.method == 'POST':
        form = DiscussionPostForm(request.POST)
        if form.is_valid():
            discussion_post = form.save(commit=False)
            discussion_post.author = request.user
            discussion_post.save()
            return redirect('discussions')
    else:
        form = DiscussionPostForm()
    discussion_posts = DiscussionPost.objects.all().order_by('-date_posted')
    return render(request, 'discussions.html', {'form': form, 'discussion_posts': discussion_posts})


@login_required(login_url="login")
def discussion_post_comment(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    if request.method == 'POST':
        comment_content = request.POST.get('comment')
        if comment_content:
            DiscussionComment.objects.create(post=post, author=request.user, content=comment_content)
            return redirect('discussions')
    return render(request, 'discussions.html')


@login_required(login_url="login")
def discussion_like_post(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('discussions')


@login_required(login_url="login")
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.created_by = request.user
            poll.save()
            for i in range(1, 5):  # Assuming we allow up to 4 choices per poll for simplicity
                choice_text = request.POST.get(f'choice{i}', '').strip()
                if choice_text:
                    Choice.objects.create(poll=poll, choice_text=choice_text)
            return redirect('view_polls')
    else:
        form = PollForm()
    return render(request, 'create_poll.html', {'form': form})



def view_polls(request):
    polls = Poll.objects.all()
    poll_data = []
    comment_form = PollCommentForm()  # Instantiate your comment form here

    for poll in polls:
        form = PollCommentForm()
        choices = poll.choices.all()
        total_votes = sum(choice.vote_count for choice in choices)
        results = [{'choice_text': choice.choice_text, 'percentage': (choice.vote_count / total_votes) * 100 if total_votes > 0 else 0} for choice in choices]
        poll_data.append({'poll': poll, 'results': results, 'comment_form': comment_form})

    return render(request, 'view_polls.html', {'poll_data': poll_data})



@login_required(login_url="login")
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = poll.choices.get(pk=request.POST['vote'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'view_polls.html', {
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
        return render(request, 'view_polls.html', {'form': form, 'poll': poll})


def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    has_voted = Vote.objects.filter(poll=poll, voted_by=request.user).exists()

    context = {
        'poll': poll,
        'has_voted': has_voted
    }
    return render(request, 'view_polls.html', context)