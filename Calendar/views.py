from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
import json
import math


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
        meetCount = Meeting.objects.filter(userid=int(request.session['user'])).count()
        taskCount = Task.objects.filter(userid=int(request.session['user'])).count()
        recordsPerPage = int(context['metadata']['recordsPerPage'])
        linksPerPage = int(context['metadata']['perpageLinks'])
        if 'page' in request.GET:
            context['currPage'] = int(request.GET['page'])
            currPage = context['currPage']
            if 'type' in request.GET:
                if request.GET['type'] == context['eventTypes']['Meeting']:
                    if currPage <= math.ceil(meetCount/recordsPerPage) and currPage > 0:
                        if currPage >= math.ceil(linksPerPage/2) and currPage <= math.ceil(meetCount/recordsPerPage) - math.floor(linksPerPage/2):
                            context['totalPagesMeeting'] = list(range(currPage-math.floor(linksPerPage/2), currPage+math.ceil(linksPerPage/2)))
                        elif currPage < math.ceil(linksPerPage/2):
                            context['totalPagesMeeting'] = list(range(1, math.ceil(meetCount/recordsPerPage) + 1))[:linksPerPage]
                        else:
                            context['totalPagesMeeting'] = list(range(1, math.ceil(meetCount/recordsPerPage) + 1))[-linksPerPage:]
                    else:
                        messages.warning(request, "Invalid Page Requested!")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
                    if currPage > 1:
                        context['prevMeet'] = currPage - 1
                    elif currPage > 0:
                        context['prevMeet'] = '#'
                    if currPage == math.ceil(meetCount/recordsPerPage):
                        context['nextMeet'] = '#'
                    else:
                        context['nextMeet'] = currPage + 1
                    context['meetings'] = Meeting.objects.filter(userid=int(request.session['user']))[(currPage-1)*recordsPerPage:(currPage*recordsPerPage)]
                    context['currMeetPage'] = currPage
                elif request.GET['type'] == context['eventTypes']['Task']:
                    if currPage <= math.ceil(taskCount/recordsPerPage) and currPage > 0:
                        if currPage >= math.ceil(linksPerPage/2) and currPage <= math.ceil(taskCount/recordsPerPage) - math.floor(linksPerPage/2):
                            context['totalPagesTask'] = list(range(currPage-math.floor(linksPerPage/2), currPage+math.ceil(linksPerPage/2)))
                        elif currPage < math.ceil(linksPerPage/2):
                            context['totalPagesTask'] = list(range(1, math.ceil(taskCount/recordsPerPage) + 1))[:linksPerPage]
                        else:
                            context['totalPagesTask'] = list(range(1, math.ceil(taskCount/recordsPerPage) + 1))[-linksPerPage:]
                    else:
                        messages.warning(request, "Invalid Page Requested!")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
                    if currPage > 1:
                        context['prevTask'] = currPage - 1
                    elif currPage > 0:
                        context['prevTask'] = '#'
                    if currPage == math.ceil(taskCount / recordsPerPage):
                        context['nextTask'] = '#'
                    else:
                        context['nextTask'] = currPage + 1
                    context['tasks'] = Task.objects.filter(userid=int(request.session['user']))[(currPage-1)*recordsPerPage:(currPage*recordsPerPage)]
                    context['currTaskPage'] = currPage
        else:
            context['totalPagesMeeting'] = list(range(1, math.ceil(meetCount/recordsPerPage) + 1))[:linksPerPage]
            context['totalPagesTask'] = list(range(1, math.ceil(taskCount/recordsPerPage) + 1))[:linksPerPage]
            context['tasks'] = Task.objects.filter(userid=int(request.session['user']))[:recordsPerPage]
            context['meetings'] = Meeting.objects.filter(userid=int(request.session['user']))[:recordsPerPage]
            context['prevMeet'] = '#'
            context['prevTask'] = '#'
            context['currPage'] = 1
            context['currTaskPage'] = 1
            context['currMeetPage'] = 1
            if meetCount > recordsPerPage:
                context['nextMeet'] = context['currPage'] + 1
            else:
                context['nextMeet'] = '#'
            if taskCount > recordsPerPage:
                context['nextTask'] = context['currPage'] + 1
            else:
                context['nextTask'] = '#'
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
                elif request.GET['type'] == context['eventTypes']['Task']:
                    taskObj = Task.objects.filter(id=int(request.GET['id'])).first()
                    if taskObj.userid == int(request.session['user']):
                        Task.objects.filter(id=int(request.GET['id'])).first().delete()
                        messages.success(request, f"Task deleted successfully!")
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
                if 'id' in request.GET:
                    context['allTasks'] = Task.objects.filter(userid=int(request.session['user']))
                    flag = False
                    context['tasks'] = list()
                    context['taskGroupTitle'] = list()
                    for task in context['allTasks']:
                        if task.taskGroup not in context['taskGroupTitle'] and len(task.taskGroup) > 0:
                            context['taskGroupTitle'].append(task.taskGroup)
                        if task.id == int(request.GET['id']):
                            flag = True
                            context['taskDetails'] = task
                        else:
                            context['tasks'].append(task)
                    if not flag:
                        context['taskDetails'] = False
                        messages.warning(request, "Requested Task not found!")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
                    context['task'] = True
                    context['meeting'] = False
                    context['view'] = True
                    return render(request, f"{context['metadata']['alphaApp']}/showEvent.html", context=context)
                else:
                    return redirect(f"/{context['mappingUrls']['prefix']}")
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
                context['tasks'] = Task.objects.filter(userid=int(request.session['user']))
                context['taskGroups'] = Task.objects.filter(userid=int(request.session['user'])).distinct('taskGroup').values_list('taskGroup', flat=True)
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
                if 'meetNote' in request.POST:
                    meeting.meetingNotes = str(request.POST['meetNote']).strip()
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
                date = request.POST['date']
                time = request.POST['time']
                taskGrp = request.POST['taskGrp']
                if taskGrp == '0':
                    if 'grpTitle' in request.POST:
                        grpTitle = str(request.POST['grpTitle']).strip()
                elif taskGrp == '-1':
                    grpTitle = ""
                else:
                    grpTitle = str(request.POST['taskGrp']).strip()
                title = request.POST['title']
                desc = request.POST['desc']
                taskRef = 0
                if 'taskRef' in request.POST:
                    if int(request.POST['taskRef']) == 0:
                        taskRef = 0
                    elif int(request.POST['taskRef']) > 0:
                        taskRef = int(request.POST['taskRef'])
                if 'taskID' in request.POST:
                    task = Task.objects.filter(id=int(request.POST['taskID'])).first()
                    if task.userid != int(request.session['user']):
                        messages.warning(request, "Illegal Operation!")
                        return redirect(f"/{context['mappingUrls']['prefix']}")
                else:
                    task = Task()
                task.time = time
                task.date = date
                task.title = title
                task.taskGroup = grpTitle
                task.description = desc
                task.refTask = taskRef
                task.userid = int(request.session['user'])
                if 'taskNote' in request.POST:
                    taskNote = str(request.POST['taskNote']).strip()
                    task.taskNotes = taskNote
                if 'taskID' in request.POST:
                    task.save()
                    messages.success(request, f"Task {task.title} updated successfully!")
                    return redirect(f"/{context['mappingUrls']['prefix']}{context['mappingUrls']['show']}?type={context['eventTypes']['Task']}&id={task.id}")
                else:
                    task.save()
                    messages.success(request, f"New task {task.title} added successfully!")
                    return redirect(f"/{context['mappingUrls']['prefix']}")
    else:
            messages.warning(request, "Invalid Operation!")
            return redirect(f"/{context['mappingUrls']['prefix']}")
