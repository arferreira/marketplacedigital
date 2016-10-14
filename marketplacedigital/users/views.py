from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from .forms import RegistrationForm
from .models import Profile

import hashlib
import random
import datetime

def register(request):
    if request.user.is_authenticated():
        return redirect('/')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print('Form is valid')
            #datas['email_path']="/ActivationEmail.txt"
            #datas['email_subject']="Activation de votre compte yourdomain"
            # form.sendEmail(datas)

            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            user.save()

            # Generation of an activation key based on the username of the new user
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            usernamesalt = user.username
            complete_salt = salt + usernamesalt
            complete_salt = complete_salt.encode('utf8')

            print(complete_salt)

            profile = Profile.objects.get(user=user)
            profile.activation_key = hashlib.sha1(complete_salt).hexdigest()
            profile.key_expiration = (datetime.datetime.strftime(datetime.datetime.now() +
                datetime.timedelta(days=7), "%Y-%m-%d %H:%M:%S"))
            profile.activated = False

            profile.save()

            request.session['registered']=True #For display purposes
            return redirect('/')
    else:
        form = RegistrationForm() #Display form with error messages (incorrect fields, etc)
        print(form.errors)
    return render(request, 'users/register.html', locals())

#View called from activation email. Activate user if link didn't expire (48h default), or offer to
#send a second link if the first expired.
def activation(request, key):
    activation_expired = False
    already_active = False
    profile = get_object_or_404(Profile, activation_key=key)
    if profile.user.is_active == False:
        if timezone.now() > profile.key_expires:
            activation_expired = True #Display: offer the user to send a new activation link
            id_user = profile.user.id
        else: #Activation successful
            profile.user.is_active = True
            profile.user.save()

    #If user is already active, simply display error message
    else:
        already_active = True #Display : error message
    return render(request, 'siteApp/activation.html', locals())

def new_activation_link(request, user_id):
    form = RegistrationForm()
    datas={}
    user = User.objects.get(id=user_id)
    if user is not None and not user.is_active:
        datas['username']=user.username
        datas['email']=user.email
        datas['email_path']="/ResendEmail.txt"
        datas['email_subject']="Nouveau lien d'activation yourdomain"

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        usernamesalt = datas['username']
        if isinstance(usernamesalt, unicode):
            usernamesalt = usernamesalt.encode('utf8')
        datas['activation_key']= hashlib.sha1(salt+usernamesalt).hexdigest()

        profile = Profile.objects.get(user=user)
        profile.activation_key = datas['activation_key']
        profile.key_expires = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
        profile.save()

        form.sendEmail(datas)
        request.session['new_link']=True #Display: new link sent

    return redirect('/')