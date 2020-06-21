#!/usr/bin/env python3

import os
from flask import Flask,session,render_template,request,redirect,flash,jsonify
from jinja2 import Template
from flask_session import Session
from flask_socketio import SocketIO, emit,join_room,leave_room
from login import *
import itertools
from collections import deque

app = Flask(__name__)

# Configure session to use filesystem

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

#Initialize socketio

socketio = SocketIO(app)

#Global variables to store user data

#Some predefined messages and channels to display beforehand.

channels={'College Group':["Suhail","Mark"],'School Group':["Irfan"],'Games zone':["Irfan"],'Stackoverflow':["Suhail","Bucky","Mark"]}

messages={'College Group': deque([{'user': 'Mark', 'message': 'Hello everyone!', 'date': '21 Jun 2020', 'time': '11:24 AM', 'id': 0}, {'user': 'Suhail', 'message': 'Hey Mark!', 'date': '21 Jun 2020', 'time': '11:24 AM', 'id': 1}, {'user': 'Suhail', 'message': 'How are you doing??', 'date': '21 Jun 2020', 'time': '11:24 AM', 'id': 2}, {'user': 'Mark', 'message': 'Im doing great man! How about you?', 'date': '21 Jun 2020', 'time': '11:25 AM', 'id': 3}, {'user': 'Suhail', 'message': 'I am doing amazingly Well!', 'date': '21 Jun 2020', 'time': '11:27 AM', 'id': 4}, {'user': 'Mark', 'message': 'Sounds good to hear!', 'date': '21 Jun 2020', 'time': '11:28 AM', 'id': 5}],maxlen=100), 'School Group': deque([],maxlen=100), 'Games zone': deque([],maxlen=100), 'Stackoverflow': deque([{'user': 'Suhail', 'message': 'Hello guys!', 'date': '21 Jun 2020', 'time': '11:28 AM', 'id': 6}, {'user': 'Bucky', 'message': 'Hey suhail.', 'date': '21 Jun 2020', 'time': '11:29 AM', 'id': 7}, {'user': 'Suhail', 'message': 'Did you checkout my new chatroom ?', 'date': '21 Jun 2020', 'time': '11:30 AM', 'id': 8}, {'user': 'Bucky', 'message': 'Yeah man.It was cool', 'date': '21 Jun 2020', 'time': '11:30 AM', 'id': 9}, {'user': 'Suhail', 'message': 'How about Mark?', 'date': '21 Jun 2020', 'time': '11:30 AM', 'id': 10}, {'user': 'Bucky', 'message': 'I believe he would have checked it', 'date': '21 Jun 2020', 'time': '11:31 AM', 'id': 11}],maxlen=100)}

#PRIMARY_KEY
i=12


@app.route("/",methods=['POST','GET'])
def login():
    prev_user=False
    if request.method=='GET':
        return render_template("login.html")
    if request.method=='POST':

        #TO retrive previous user's session
        prev_user=request.form.get("puser").capitalize() if(request.form.get("puser")) else None

    name=request.form.get("username").capitalize() if(request.form.get("username")) else None
    session["uname"]=prev_user if(prev_user) else name  #Add current/previous session user to session variable

    return redirect('/index')



@app.route("/index")
@login_required
def index():

    #Route which lists channels in which the current user is a participant.

    return render_template("index.html",user=session["uname"],channels=channels)



@app.route("/rooms")
@login_required
def rooms():

    #Route which lists all the available channels in the website.

    return render_template("rooms.html",user=session["uname"])



@app.route("/roompage/<channelName>")
@login_required
def roompage(channelName):

    #This page displays the previous messages of the channel and also updates them when new messages arrive.

    return render_template("roompage.html",channel=channelName,participants=channels[channelName],user=session["uname"])



#Route for handling AJAX requests
@app.route("/ajax/<args>",methods=['POST','GET'])
def ajax(args):

    #For handling AJAX request to check rooms

    if args=="room":

        #A GET request to extract all the channels created in the website.

        if request.method=='GET':
            return channels

        else:

            #A POST request to know if the channelName aldready exists in the website.

            channelName=request.form.get('name').capitalize()
            if channelName in channels:
                return 'NOK'
            else:

                #If the channelName is new and is not aldready taken then it is updated to the server's global variable.

                channels.update({channelName:[session["uname"]]})

                #Creating a list to store the messages of the channel being created.

                messages[channelName]=deque(maxlen=100)
                return 'OK'

    #For handling AJAX request to check participants

    if args=="participants":
        channelName=request.form.get('name')

        #Add user to channel users list.

        channels[channelName].append(session["uname"])
        return 'OK'



@app.route("/messages/<channelName>",methods=['GET'])
def msgs(channelName):
    #Return JSON version of messages to display in the roompage.
    if messages[channelName]==[] :
        return '0'
    else:
        return jsonify(list(messages[channelName]))

#Socket to capture,store and broadcast new messages.

@socketio.on("new message")
def new_message(data):


    #slice the required contents from the data and push it to the messages dict.

    d=dict(itertools.islice(data.items(),1,len(data)))

    #i is the id ( PRIMARY_KEY ) for each message

    global i
    d.update({'id':i})
    data.update({'id':i})
    i+=1

    messages[data['channelName']].append(d)

    #Broadcast the message to all participants in the Channel.

    emit('message received',data,broadcast=True)

#Socket to delete messages.

@socketio.on("delete_msg")
def delete_message(data):

    #Search and compare the primary keys(id) of message to be deleted.

    for i in range(len(messages[data['channelName']])):

        #Delete the message from server if the primary keys match.

        if messages[data['channelName']][i]['id']==data['msg_id']:
            del messages[data['channelName']][i]
            break

    #Delete the message to all participants in the Channel.

    emit('msg_deleted',data,broadcast=True)
