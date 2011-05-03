# version: v1
# scope: https://www.googleapis.com/auth/moderator
# title: Simple command-line example for Moderator.
# description: Command-line application that exercises the Google Moderator API.

  # Create a new Moderator series.
  series_body = {
        "description": "Share and rank tips for eating healthy and cheap!",
        "name": "Eating Healthy & Cheap",
        "videoSubmissionAllowed": False
        }
  series = service.series().insert(body=series_body).execute()
  print "Created a new series"

  # Create a new Moderator topic in that series.
  topic_body = {
        "description": "Share your ideas on eating healthy!",
        "name": "Ideas",
        "presenter": "liz"
        }
  topic = service.topics().insert(seriesId=series['id']['seriesId'],
                            body=topic_body).execute()
  print "Created a new topic"

  # Create a new Submission in that topic.
  submission_body = {
        "attachmentUrl": "http://www.youtube.com/watch?v=1a1wyc5Xxpg",
        "attribution": {
          "displayName": "Bashan",
          "location": "Bainbridge Island, WA"
          },
        "text": "Charlie Ayers @ Google"
        }
  submission = service.submissions().insert(seriesId=topic['id']['seriesId'],
      topicId=topic['id']['topicId'], body=submission_body).execute()
  print "Inserted a new submisson on the topic"

  # Vote on that newly added Submission.
  vote_body = {
        "vote": "PLUS"
        }
  service.votes().insert(seriesId=topic['id']['seriesId'],
                   submissionId=submission['id']['submissionId'],
                   body=vote_body)
  print "Voted on the submission"

