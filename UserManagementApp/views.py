from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.contrib import auth
from django.http import Http404
from UserManagementApp.forms import MyRegistrationForm
from django.contrib.auth.models import User
from UserManagementApp.models import UserLoginDatetime
from django.contrib.auth.decorators import user_passes_test


def update_user_last_login_datetime(request):
    event = UserLoginDatetime()  # creating an empty instance
    event.user_name = request.user.get_username()  # remember username in the attribute
    event.user_login_datetime = request.user.last_login
    event.save()
    return True


def login(request):
    if request.method == 'POST':
        # print("POST data =", request.POST)  # data in the 'request' object is placed in the POST attribute (dictionary)
        username = request.POST.get('login')  # from this "request" instance take POST attribute and get login
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)  # auth.authenticate returns User object or None
        # print('login -> user =', user)
        # print('last login time', user.last_login)
        if user:
            auth.login(request, user)  # logging user in
            update_user_last_login_datetime(request)
            return HttpResponseRedirect('/user/stats/')  # if we doesn't need a context
            # return login_stats(request)
            # both returns lead to main view with index.html template
            # but giving the GET method login form isn't shown
            # login view only accept POST methods
            # because of that we show form only when user is not authenticated

        else:  # if user is None, ie. user was not authenticated
            return render(request, 'index.html',
                          {'username': username, 'errors': True})  # errors:True - print 'login or pw doesn't exist'

            # return HttpResponseRedirect("/", {'errors': True}) #it's not possible to pass any arguments than path ('/') to HttpResponseRedirect
    raise Http404


@user_passes_test(lambda u: u.is_authenticated)
def user_stats(request):
    user_login_data = UserLoginDatetime.objects.filter(user_name=request.user)
    return render(request, 'user_stats.html', {'user_login_data': user_login_data})


def logout(request):
    auth.logout(request)
    return render(request, "logout.html")


def registration(request):
    if request.method == 'POST':  # check if data is sent by the POST method (all forms use POST method)
        form = MyRegistrationForm(request.POST)
        print(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
        context = {'form': form}
        return render(request, 'registration.html', context)  #
    context = {'form': MyRegistrationForm()}
    return render(request, 'registration.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_page(request):
    users = User.objects.all()
    return render(request, 'admin-page.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return HttpResponseRedirect('/admin')
