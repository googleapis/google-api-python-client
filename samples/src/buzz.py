# version: v1
# scope: https://www.googleapis.com/auth/buzz
# title: Simple command-line sample for Buzz.
# description: Command-line application that retrieves the users latest content and then adds a new entry.

  activities = service.activities()

  # Retrieve the first two activities
  activitylist = activities.list(
      max_results='2', scope='@self', userId='@me').execute()
  print "Retrieved the first two activities"

  # Retrieve the next two activities
  if activitylist:
    activitylist = activities.list_next(activitylist).execute()
    print "Retrieved the next two activities"

  # Add a new activity
  new_activity_body = {
      'title': 'Testing insert',
      'object': {
        'content':
        u'Just a short note to show that insert is working. ☄',
        'type': 'note'}
      }
  activity = activities.insert(userId='@me', body=new_activity_body).execute()
  print "Added a new activity"

  activitylist = activities.list(
      max_results='2', scope='@self', userId='@me').execute()

  # Add a comment to that activity
  comment_body = {
      "content": "This is a comment"
      }
  item = activitylist['items'][0]
  comment = service.comments().insert(
      userId=item['actor']['id'], postId=item['id'], body=comment_body
      ).execute()
  print 'Added a comment to the new activity'
  pprint.pprint(comment)
