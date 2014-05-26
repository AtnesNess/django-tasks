from django.shortcuts import render
from django.contrib.auth.forms import  UserCreationForm, AuthenticationForm
from chat.forms import RegistrationForm, InfoForm
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ObjectDoesNotExist
from chat.models import ChatUser, UserFriends, Message
from django.contrib.auth.decorators import login_required


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('chat.views.contacts'))
    post = ''
    form = AuthenticationForm(None)
    if request.method == 'POST':
        post = request.POST
        form = AuthenticationForm(None, request.POST or None)
        if form.is_valid():
            auth.login(request, form.get_user())
            return HttpResponseRedirect(reverse('chat.views.contacts'))

    return render(request,  'login.html', {'form':form })


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('chat.views.login'))


def registration(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('chat.views.contacts'))
    post = ''
    form = RegistrationForm(None)
    if request.method == 'POST':
        post = request.POST
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            user = auth.authenticate(username=post['username'],
                                     password=post['password1'])
            auth.login(request, user)
            return HttpResponseRedirect(reverse('chat.views.contacts'))
    return render(request,  'registration.html', {'form': form})


@login_required
def account(request):
    user = request.user
    form = InfoForm(initial={'status': user.status})
    if request.method == 'POST':
        post = request.POST
        form = InfoForm(request.POST, request.FILES, initial={'status': post['status']})
        if form.is_valid():
            if request.FILES:
                user.avatar = request.FILES['avatar']
            if post['status']:
                user.status = post['status']
            user.save()
        return HttpResponseRedirect(reverse('chat.views.account'))
    return render(request,  'account.html', {'user': user,
                                            'form': form})

@login_required
def contacts(request):
    user = request.user
    all_friends = False
    users = ChatUser.objects.all()
    friends = UserFriends(user.id).friend_list.all()
    if str(friends) == str(users.exclude(id=user.id)):
       all_friends = True
    knocking = []
    waiting = []
    unread = {}
    for u in users:
        if (not u in UserFriends(user.id).friend_list.all() and
            user in UserFriends(u.id).friend_list.all()):
            knocking.append(u)
        if (u in UserFriends(user.id).friend_list.all() and
            not user in UserFriends(u.id).friend_list.all()):
            waiting.append(u)
        messages_unread = Message.objects.filter(to_user=user, from_user=u, is_read=False)
        unread[u.id] = 0
        for i in messages_unread:
            unread[u.id] += 1




    return render(request,  'chat/contacts.html', { 'users': users,
                                                    'user': user,
                                                    'friends': friends,
                                                    'knokings': knocking,
                                                    'waiting': waiting,
                                                    'all_friends': all_friends,
                                                    'unread': unread.items(),

                                                        })
@login_required
def add_to_friends(request, name):
    user = request.user
    friend = ChatUser.objects.get(username=name)
    UserFriends(user.id).friend_list.add(ChatUser(friend.id))
    return HttpResponseRedirect('/contacts')


@login_required
def remove_from_friends(request, name):
    user = request.user
    friend = ChatUser.objects.get(username=name)
    UserFriends(user.id).friend_list.remove(ChatUser(friend.id))
    UserFriends(friend.id).friend_list.remove(ChatUser(user.id))
    return HttpResponseRedirect(reverse('chat.views.contacts'))


@login_required
def reject(request, name):
    user = request.user
    friend = ChatUser.objects.get(username=name)
    UserFriends(friend.id).friend_list.remove(ChatUser(user.id))
    return HttpResponseRedirect(reverse('chat.views.contacts'))


@login_required
def chat_with(request, name):
    user = request.user
    try:
        friend = ChatUser.objects.get(username=name)
    except ObjectDoesNotExist:
         return HttpResponseRedirect(reverse('chat.views.contacts'))
    if (not friend in UserFriends(user.id).friend_list.all() or
         not user in UserFriends(friend.id).friend_list.all()):
        return HttpResponseRedirect(reverse('chat.views.contacts'))
    messages_unread = Message.objects.filter(to_user=user, from_user=friend, is_read=False)
    for mes in messages_unread:
        mes.is_read = True
        mes.save()
    if request.method == 'POST':
        post = request.POST

        m = Message(
            message=post['message'],
            from_user=user,
            to_user=friend,
            datetime=datetime.datetime.today()
            )
        m.save()
    messages = Message.objects.filter(to_user=friend, from_user=user) |\
               Message.objects.filter(to_user=user, from_user=friend)


    return render(request,  'chat/chat.html', {'user': user,
                                               'friend': friend,
                                               'messages': messages})

@login_required
def unread_with(request, name):
    user = request.user
    try:
        friend = ChatUser.objects.get(username=name)
    except ObjectDoesNotExist:
         return HttpResponseRedirect(reverse('chat.views.contacts'))
    messages_unread = Message.objects.filter(to_user=user, from_user=friend, is_read=False)
    unread = len(messages_unread)

    return HttpResponse(unread)