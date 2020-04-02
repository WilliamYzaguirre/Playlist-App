'''
Created on Dec, 201

@author: Will Yzaguirr
'''
from flask import Flask, flash, render_template, request, session
import os
import json
from app import app

app.secret_key = os.urandom(12)


current_user = ""

'''set global variable user_info with a dictionary of usernames and 
passwords'''
with open('users.json', 'r') as jsonfile:
    user_data = json.loads(jsonfile.read())
users = [users['username'] for users in user_data]
passwords = [passw['password'] for passw in user_data]
user_info = dict(zip(users, passwords))

'''creates 2 global variables, songs, which is the available songs 
to add to playlist, and all_songs which is all the songs. Used for
getting full song info'''
with open('songs.json', 'r') as jsonfile:
    song_data = json.loads(jsonfile.read())
songs = [(info['songname'], info['artist'], info['year'], info['album_cover']) for info in song_data]
all_songs = songs

'''create global variable user_playlist which is a dictionary with users 
and their playlist in song title form'''
temp = []
user_playlist = []
playlists = [songs['playlist'] for songs in user_data]
for userP in playlists:
    for sng in userP:
        for titles in songs:
            if sng in titles:
                temp.append(titles)
    user_playlist.append(temp)
    temp = []

user_playlist = dict(zip(users, user_playlist))


@app.route('/')
def home():
    '''if you're not logged in, return the login page. Otherwise, 
    return the playlist display page'''
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        global current_user
        order = []
        for i in range(0, len(user_playlist.get(current_user))):
            order.append(i + 1)
        return render_template("user_playlist.html", 
                               playlist_length=len(user_playlist.get(current_user)),
                               current_user=current_user,
                               playlist=user_playlist.get(current_user),
                               all_songs=songs,
                               order = order)


@app.route('/login', methods=['POST'])
def do_admin_login():
    '''gets submitted username and password and checks if they match
    a user'''
    global current_user
    current_user = request.form['username']
    if request.form['username'] in user_info.keys() and request.form['password'] == user_info.get(request.form['username']):
        session['logged_in'] = True
    else:
        flash('incorrect login')
    return home()


@app.route("/logout")
def logout():
    '''logs out user'''
    session['logged_in'] = False
    return home()

@app.route("/submit")
def submit_changes():
    '''when submit is clicked, perform actions given in dropdown menu'''
    print("Songs:", songs)
    print("User play:", user_playlist)
    '''get dictionary change_log of song and action(add, remove)'''
    if request.method == "GET":
        current_user = request.args.get("user_info")

        if request.args.get("move") != "":
            start, end = request.args.get("move").split("_")[1] , request.args.get("move").split("_")[2]
            print(start, end)
            temp = user_playlist.get(current_user)[int(start) - 1]
            user_playlist.get(current_user)[int(start) - 1] = user_playlist.get(current_user)[int(end) - 1]
            user_playlist.get(current_user)[int(end) - 1] = temp

        change_log = {}
        for song in songs:
            if request.args.get(song[0].split(" ")[0]) != "nothing":
                change_log[song[0]] = request.args.get(song[0].split(" ")[0])

        print("CHange:", change_log)
        print("Current pl:", user_playlist.get(current_user))

        #to_del holds the place of the songs in user_playlist to be deleted
        to_del = []
        for song, action in change_log.items():  
            if action == "remove":
                for i in range(len(user_playlist.get(current_user))):
                    print(i)
                    if song in user_playlist.get(current_user)[i]:
                        to_del.append(i)
                del user_playlist.get(current_user)[to_del[0]]
            else:
                temp = []
                for music in songs:
                    if song in music:
                        temp.append(music)
                user_playlist.get(current_user).append(temp[0])
        print("Changed play:", user_playlist.get(current_user))

        '''creates playlist of song titles to be written to json'''

        new_json_playlist = []
        for song_iter in user_playlist.get(current_user):
            new_json_playlist.append(song_iter[0])

        '''rewrites the json file with updated playlist info'''

        filename = 'users.json'
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        for users in data:
            if users['username'] == current_user:
                users['playlist'] = new_json_playlist

        os.remove(filename)
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        order = []
        for i in range(0, len(user_playlist.get(current_user))):
            order.append(i + 1)

        return render_template("user_playlist.html", 
                               playlist_length = len(user_playlist.get(current_user)),
                               current_user = current_user, 
                               playlist = user_playlist.get(current_user),
                               all_songs = songs,
                               order = order)

    else:
        order = []
        for i in range(0, len(user_playlist.get(current_user))):
            order.append(i + 1)
        return render_template("user_playlist.html", 
                               playlist_length = len(user_playlist.get(current_user)),
                               current_user = current_user, 
                               playlist = user_playlist.get(current_user),
                               all_songs = songs,
                               order = order)
