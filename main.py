import instagrapi
import json
import os
import copy
import re

def parsePostUrl(url):
    if url[-1] == '/':
        url = url[:-1]

    return url.split('/')[-1]

def getCommentId(comments, username):
    for comment in comments:
        if comment.user.username == username:
            return comment.pk

# targetComment = 17964502327860774

successfulLikes = 0
unsuccesfulLikes = 0

commentId = 0

# Read sessions json
accounts = {}
if os.path.exists('sessions.json'):
    with open('sessions.json', 'r') as f:
        sessions = json.load(f)

# Iterate through accounts in accounts.csv
with open('accounts.csv', 'r') as accountsCsv:
    for line in accountsCsv:
        # Get account details
        account = line.strip().split(',')
        username = account[0]
        password = account[1]

        # Check if account session exists in sessions.json
        if username in sessions:
            # Load session
            cl_session = sessions[username]
        else:
            cl_session =  {}

        # Load session into client to avoid authentication blocks
        cl = instagrapi.Client(cl_session)

        # Attempt to log in to account
        try:
            loggedIn = cl.login(username, password)
            if loggedIn:
                print("Logged in as user: " + username)
        except Exception as e:
            print("Failed to login to account: " + username)
            loggedIn = False
            unsuccesfulLikes += 1

        # Check if login was successful
        if loggedIn:
            # Like target comment
            try:
                if(not commentId):
                    # Ask for instagram post url
                    url = input("Enter Instagram post url (example: https://www.instagram.com/p/aaaaaaa/): ")

                    # Ask for username of user who posted the comment
                    commenterUsername = input("Enter username of user who posted the comment: ")

                    postId = cl.media_id(cl.media_pk_from_url(url))

                    # Get all comments from post
                    comments = cl.media_comments(postId, 1000)

                    # Get comment id based on post id and username who commented
                    commentId = getCommentId(comments, commenterUsername)

                    print(commentId)
                likeSuccessful = cl.comment_like(commentId)
                print("Liked comment: " + str(commentId) + " with account: " + username)
                successfulLikes += 1
            except Exception as e:
                print("Failed to like comment: " + str(commentId) + " with account: " + username)
                print(e)
                unsuccesfulLikes += 1

            with open('sessions.json', 'w') as settingsWriteFile:
                # Save session
                sessions[username] = cl.get_settings()
                json.dump(sessions, settingsWriteFile)

            # Clean up
            del cl
            
print("Successful likes: " + str(successfulLikes))
print("Unsuccessful likes: " + str(unsuccesfulLikes))

