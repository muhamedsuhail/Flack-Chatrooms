#!/usr/bin/env python3

import os
from flask import Flask,session,render_template,request,redirect,flash,jsonify
from jinja2 import Template
from flask_session import Session
from flask_socketio import SocketIO, emit,join_room,leave_room
from login import *
import itertools

app = Flask(__name__)

# Configure session to use filesystem

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

#Initialize socketio

socketio = SocketIO(app)

#Global variables to store user data


channels={'College Group':["Suhail"],'School Group':["Irfan"],'Games zone':["Irfan"],'Stackoverflow':["Suhail"]}
messages={'College Group':[],'School Group':[],'Games zone':[],'Stackoverflow':[]}
i=0


@app.route("/",methods=['POST','GET'])
def login():
    if request.method=='GET':
        return render_template("login.html")

    name=request.form.get("username").capitalize()
    session["uname"]=name  #Add current user to session variable

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

                messages[channelName]=[]
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
        return jsonify(messages[channelName])

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
            messages[data['channelName']].pop(i)
            break

    #Delete the message to all participants in the Channel.

    emit('msg_deleted',data,broadcast=True)
