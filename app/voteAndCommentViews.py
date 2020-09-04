from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .helper_functions import get_user, send_notifs
from math import ceil

from app.serializers import (
    CommentSerializer,
    IdeaSerializer
)

from .models import (
    Idea,
    Comment,
    Vote,
    User,
    UserFCMDevice
)


# View for both upvoting and downvoting
class VoteView(APIView):

    def post(self, request):

        # Getting data from request
        idea_keys = {"PENDING": 0, "PUBLISHED": 1, "REJECTED": 2}
        keys = {"UPVOTE": 1, "DOWNVOTE": -1}
        req_data = request.data
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "You need to login to perform this action !"}, status=status.HTTP_403_FORBIDDEN)

        # Checking if the idea with idea_id exists
        try:
            idea = Idea.objects.get(id=req_data["idea_id"])
        except Idea.DoesNotExist:
            return Response({"message": "Invalid Idea Id"}, status=status.HTTP_400_BAD_REQUEST)

        # Checking if the ida with idea_id can be voted or not
        if idea.is_reviewed == idea_keys["PENDING"] or idea.is_reviewed == idea_keys["REJECTED"]:
            return Response({"message": "Idea cannot be voted"}, status=status.HTTP_400_BAD_REQUEST)

        # Voting idea
        try:
            # Checking if the user has voted earlier (also was it upvote or downvote)
            vote = Vote.objects.get(
                user_id=user.id, idea_id=req_data["idea_id"])
            check1 = (vote.vote_type == keys["UPVOTE"] and int(
                req_data['vote_type']) == keys["UPVOTE"])
            check2 = (vote.vote_type == keys["DOWNVOTE"] and int(
                req_data['vote_type']) == keys["DOWNVOTE"])

            if check1 or check2:
                return Response({"message": "You have already Voted"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Patch for votes hack - [1UC1F3R616 26-08-2020] - PatchCode: Luci1

                # Patch Summary
                # check1 and check2 above gives false is vote is above 1 but positive
                # which means code is not break and vote is allowed.
                # Code now passes to votes model and is getting added or subtracted
                # with the value sended

                # Old code is commented below
                # idea.votes = idea.votes + int(req_data['vote_type'])
                # idea.save()
                # vote.vote_type = req_data["vote_type"]
                # vote.save()
                # idea_serializer = IdeaSerializer(idea)
                # return Response(status=status.HTTP_200_OK)
                # Updating votes in idea as well as vote object
                if req_data['vote_type'] < 1:
                    idea.votes = idea.votes - 1
                    idea.save()
                    vote.vote_type = req_data["vote_type"]
                    vote.save()
                    idea_serializer = IdeaSerializer(idea)
                    return Response(status=status.HTTP_200_OK)
                elif req_data['vote_type'] >= 1:
                    idea.votes = idea.votes + 1
                    idea.save()
                    vote.vote_type = req_data["vote_type"]
                    vote.save()
                    idea_serializer = IdeaSerializer(idea)
                    return Response(status=status.HTTP_200_OK)

        except Vote.DoesNotExist:
            # Updating Votes for idea and creating a new idea object

            vote = Vote()
            vote.user_id = user
            vote.idea_id = idea
            if req_data['vote_type'] < 1:
                idea.votes = idea.votes - 1
                vote.vote_type = -1
            elif req_data['vote_type'] >= 1:
                idea.votes = idea.votes + 1
                vote.vote_type = 1
            idea.save()
            vote.save()
            idea_serializer = IdeaSerializer(idea)
            return Response(status=status.HTTP_200_OK)


# View for posting a comment for an idea and also getting comments for idea
class CommentView(APIView):

    def get(self, request, pk):

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        total_pages = 0

        # Getting all comments
        comments = list(Comment.objects.filter(idea_id=pk))
        response = []
        if len(comments) == 0:
            return Response({"message": "There are no comments", 'total_pages': total_pages}, status=status.HTTP_204_NO_CONTENT)
        else:
            # Adding parent comment for each thread
            comments = list(Comment.objects.filter(
                parent_comment_id=None, idea_id=pk))
            serializer = CommentSerializer(comments, many=True)

            total_pages = ceil(len(serializer.data)/5)

            if offset == None or offset == "":
                response = serializer.data
            else:
                response = serializer.data[start:end]

            if len(response) == 0:
                return Response({"message": "There are no comments", 'total_pages': total_pages}, status=status.HTTP_204_NO_CONTENT)

            # Adding child comment for each thread
            for resp in response:
                user = User.objects.get(id=resp['user_id'])
                resp['username'] = user.username
                resp['child_comments'] = None
                child_comments = list(Comment.objects.order_by(
                    'date_time').filter(parent_comment_id=resp['id'], idea_id=pk))
                child_comment_serializer = CommentSerializer(
                    child_comments, many=True)
                resp['child_comments'] = child_comment_serializer.data
                for comm in resp['child_comments']:
                    childUser = User.objects.get(id=comm['user_id'])
                    comm['username'] = childUser.username

            return Response({"message": response, 'total_pages': total_pages}, status=status.HTTP_200_OK)

    def post(self, request):
        keys = {"PENDING": 0, "PUBLISHED": 1, "REJECTED": 2}
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "You need to login to perform this action !"}, status=status.HTTP_403_FORBIDDEN)

        request.data['user_id'] = user.id

        # Checking if an idea with idea_id exists
        try:
            idea = Idea.objects.get(
                id=(request.data)['idea_id'], is_reviewed=keys["PUBLISHED"])
        except:
            return Response({"message": "Invalid Idea Id"}, status=status.HTTP_400_BAD_REQUEST)

        # Validating and saving comment for that idea
        comment = CommentSerializer(data=request.data)
        if comment.is_valid():
            comment.save()

            response = comment.data
            registration_ids = []

            # Getting Registration ids
            response['username'] = user.username

            try:
                ideaUserFCMDevice = UserFCMDevice.objects.get(
                    user_id=idea.user_id.id)
                if not (user.id == ideaUserFCMDevice.user_id.id):
                    registration_ids.append(ideaUserFCMDevice.registration_id)
            except UserFCMDevice.DoesNotExist:
                pass

            if response['parent_comment_id'] == None:
                # Main Thread Comment
                response['child_comments'] = []
            else:
                # Child Comment
                response['child_comments'] = None
                try:
                    parentComment = Comment.objects.get(
                        id=response['parent_comment_id'])
                    parentCommentUserFCMDevice = UserFCMDevice.objects.get(
                        user_id=parentComment.user_id.id)
                    if not(parentCommentUserFCMDevice.registration_id in registration_ids):
                        if not(parentCommentUserFCMDevice.user_id.id == user.id):
                            registration_ids.append(
                                parentCommentUserFCMDevice.registration_id)
                except UserFCMDevice.DoesNotExist:
                    pass

            # Sending Notifications
            message_title = user.username + " Commented"
            message_body = response['body']
            data = {
                "url": "https://ideas.dscvit.com/ideas/" + str(idea.id) + "/"
            }

            result = send_notifs(
                registration_ids, message_title, message_body, data)

            if result:
                print("Failed to send notification")

            return Response({"message": response}, status=status.HTTP_200_OK)
        else:
            return Response({"message": comment.errors}, status=status.HTTP_400_BAD_REQUEST)


class MyCommentsView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "You need to login to perform this action !"}, status=status.HTTP_403_FORBIDDEN)

        comments = Comment.objects.filter(
            user_id=user.id).order_by('-date_time')
        serializer = CommentSerializer(comments, many=True)
        serializer = serializer.data
        if len(serializer) == 0:
            return Response({"message": "No Comments found"}, status=status.HTTP_204_NO_CONTENT)

        for comment in serializer:
            comment['idea_title'] = Idea.objects.get(
                id=comment['idea_id']).project_title

        return Response({"message": "Comments Found", "comments": serializer}, status=status.HTTP_200_OK)
