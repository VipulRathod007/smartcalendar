from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
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
        context['meetings'] = Meeting.objects.filter(userid=int(request.session['user']))
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
                    request.session['user'] = User.objects.filter(email=emailAddr).first().id
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
                    userObj.username = emailAddr
                    userObj.password = passwd
                    userObj.save()
                    request.session['user'] = userObj.id
                    context['subTitle'] = "Home"
                    return redirect(f"/{context['mappingUrls']['prefix']}")


def logout(request):
    request.session['user'] = None
    request.session.pop('user')
    context['subTitle'] = "Home"
    messages.info(request, 'Logged out successfully!')
    return redirect(f"/{context['mappingUrls']['prefix']}")


# def updateEvent(request):
#     if 'user' in request.session:
#         if request.method == "POST":
#             if 'meetID' in request.POST and 'event' in request.POST:
#                 if request.POST['event'] == context['eventTypes']['Meeting']:
#                     meetObj = Meeting.objects.filter(id=int(request.POST['meetID'])).first()
#                     if meetObj.userid == int(request.session['user']):
#                     else:
#                         messages.warning(request, "Illegal Operation")
#                         return redirect(f"/{context['mappingUrls']['prefix']}")
#             else:
#                 messages.warning(request, "Important Parameter missing!")
#                 return redirect(f"/{context['mappingUrls']['prefix']}")
#         else:
#             return redirect(f"/{context['mappingUrls']['prefix']}")
#     else:
#         return redirect(f"/{context['mappingUrls']['prefix']}")


def deleteEvent(request):
    if 'user' in request.session:
        if request.method == "GET":
            if 'id' in request.GET and 'type' in request.GET:
                if request.GET['type'] == context['eventTypes']['Meeting']:
                    meetObj = Meeting.objects.filter(id=int(request.GET['id'])).first()
                    if meetObj.userid == int(request.session['user']):
                        Meeting.objects.filter(id=int(request.GET['id'])).first().delete()
                        messages.success(request, f"Meeting deleted successfully!")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
                    else:
                        messages.warning(request, "Illegal Operation")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
            else:
                messages.warning(request, "Important Parameter missing!")
                return redirect(f"/{context['mappingUrls']['prefix']}")
        else:
            return redirect(f"/{context['mappingUrls']['prefix']}")
    else:
        return redirect(f"/{context['mappingUrls']['prefix']}")


def showEvent(request):
    context['subTitle'] = "Show"
    if request.method == "GET":
        if 'action' in request.GET or True:
            if 'type' in request.GET and request.GET['type'] == context['eventTypes']['Meeting']:
                if 'id' in request.GET:
                    context['allMeetings'] = Meeting.objects.filter(userid=int(request.session['user']))
                    flag = False
                    context['meetings'] = list()
                    for meet in context['allMeetings']:
                        if meet.id == int(request.GET['id']):
                            flag = True
                            context['meetingDetails'] = meet
                        else:
                            context['meetings'].append(meet)
                    if not flag:
                        context['meetingDetails'] = False
                        messages.warning(request, "Requested Meeting not found!")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
                    context['meeting'] = True
                    context['view'] = True
                    return render(request, f"{context['metadata']['alphaApp']}/showEvent.html", context=context)
                else:
                    return redirect(f"/{context['mappingUrls']['prefix']}")
            elif 'type' in request.GET and request.GET['type'] == context['eventTypes']['Task']:
                pass
    else:
        return redirect(f"/{context['mappingUrls']['prefix']}")


def add(request):
    context['subTitle'] = "Add New"
    if request.method == "GET":
        if 'eventTypes' in request.GET:
            if request.GET['eventTypes'] == context['eventTypes']['Meeting']:
                context['meeting'] = True
                context['meetings'] = Meeting.objects.filter(userid=int(request.session['user']))
                return render(request, f"{context['metadata']['alphaApp']}/addnew.html", context=context)
            else:
                context['meeting'] = False
                return render(request, f"{context['metadata']['alphaApp']}/addnew.html", context=context)
        else:
            return redirect(f"/{context['mappingUrls']['prefix']}")
    elif request.method == "POST":
        if 'event' in request.POST:
            if request.POST['event'] == context['eventTypes']['Meeting']:
                date = request.POST['date']
                time = request.POST['time']
                meetType = request.POST['meetType']
                title = request.POST['title']
                desc = request.POST['desc']
                if 'meetID' in request.POST:
                    meeting = Meeting.objects.filter(id=int(request.POST['meetID'])).first()
                    if meeting.userid != int(request.session['user']):
                        messages.warning(request, "Illegal Operation!")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
                else:
                    meeting = Meeting()
                if meetType == "0":
                    messages.warning(request, "Invalid Meeting Type!")
                    return redirect(f"/{context['mappingUrls']['prefix']}")
                elif meetType == "1":
                    meeting.meetType = "Virtual"
                    meetUrl = request.POST['meetUrl']
                    meeting.urlAddr = meetUrl
                elif meetType == "2":
                    meeting.meetType = "Visit"
                    meetAddr = request.POST['meetAddr']
                    meeting.meetAddr = meetAddr
                if 'meetRef' in request.POST:
                    if request.POST['meetRef'] == '-1':
                        messages.warning(request, "Invalid Meeting Selected!")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
                    else:
                        meeting.refMeet = int(request.POST['meetRef'])
                else:
                    meeting.refMeet = 0
                meeting.title = title
                meeting.date = date
                meeting.time = time
                meeting.description = desc
                meeting.userid = int(request.session['user'])
                if 'meetID' in request.POST:
                    if meeting.meetType == 'Virtual':
                        meeting.meetAddr = ''
                    else:
                        meeting.urlAddr = ''
                    meeting.save()
                    messages.success(request, f"{meeting.title} updated successfully!")
                    return redirect(f"/{context['mappingUrls']['prefix']}{context['mappingUrls']['show']}?type={context['eventTypes']['Meeting']}&id={meeting.id}")
                else:
                    meeting.save()
                    messages.success(request, f"New meeting {meeting.title} added successfully!")
                    return redirect(f"/{context['mappingUrls']['prefix']}")
            elif request.POST['event'] == context['eventTypes']['Task']:
                pass
        else:
            messages.warning(request, "Invalid Operation!")
            return redirect(f"/{context['mappingUrls']['prefix']}")
