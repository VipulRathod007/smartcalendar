from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
import json


with open('config.json', 'r') as file:
    jsonFile = json.load(file)
    context = jsonFile['content']


def transformUrl(inData):
    """
    :param inData: must be a dictionary
    :return: None
    """
    context['transformedUrls'] = dict()
    for attr, val in inData.items():
        context['transformedUrls'][attr] = "{% url \'" + val + "\' %}"


def home(request):
    context['subTitle'] = "Home"
    transformUrl(context['urls'])
    if 'user' in request.session:
        return render(request, f"{context['metadata']['alphaApp']}/index.html", context=context)
    else:
        return redirect(f"/{context['mappingUrls']['prefix']}{context['mappingUrls']['authenticate']}")


def authenticate(request):
    if request.method == "GET":
        if 'user' in request.session:
            return redirect(f"/{context['mappingUrls']['prefix']}")
        else:
            if 'authType' in request.GET and request.GET['authType'] == 'register':
                context['subTitle'] = "Register"
                context['login'] = False
                return render(request, f"{context['metadata']['alphaApp']}/authenticate.html", context=context)
            else:
                context['subTitle'] = "Login"
                context['login'] = True
                return render(request, f"{context['metadata']['alphaApp']}/authenticate.html", context=context)
    elif request.method == "POST":
        if 'user' in request.session:
            return redirect(f"/{context['mappingUrls']['prefix']}")
        else:
            if request.POST['authType'] == 'login':
                emailAddr = request.POST['email']
                passwd = request.POST['password']
                if User.objects.filter(email=emailAddr).first() is None:
                    messages.warning(request, "Entered Email Address not found!")
                    return redirect(f"/{context['mappingUrls']['prefix']}{context['mappingUrls']['authenticate']}")
                elif User.objects.filter(email=emailAddr).first().password != passwd:
                    messages.warning(request, "Password didn't match!")
                    return redirect(f"/{context['mappingUrls']['prefix']}{context['mappingUrls']['authenticate']}")
                else:
                    context['subTitle'] = "Home"
                    return redirect(f"/{context['mappingUrls']['prefix']}")
            else:
                emailAddr = request.POST['email']
                passwd = request.POST['password']
                if User.objects.filter(email=emailAddr).first() is not None and User.objects.filter(email=emailAddr).first().email == emailAddr:
                    messages.warning(request, "Entered Email Address has already been used!")
                    return redirect(f"/{context['mappingUrls']['prefix']}{context['mappingUrls']['register']}")
                else:
                    userObj = User()
                    userObj.email = emailAddr
                    userObj.password = passwd
                    request.session['user'] = emailAddr
                    userObj.save()
                    context['subTitle'] = "Home"
                    return redirect(f"/{context['mappingUrls']['prefix']}")


def logout(request):
    request.session['user'] = None
    request.session.pop('user')
    context['subTitle'] = "Home"
    return redirect(f"/{context['mappingUrls']['prefix']}")