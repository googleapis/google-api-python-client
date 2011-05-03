# version: v1.2
# scope: https://www.googleapis.com/auth/prediction
# title: Simple command-line sample for the Google Prediction API
# description: Command-line application that trains on some data. This sample does the same thing as the Hello Prediction! example.

  # Name of Google Storage bucket/object that contains the training data
  OBJECT_NAME = "apiclient-prediction-sample/prediction_models/languages"

  # Start training on a data set
  train = service.training()
  start = train.insert(data=OBJECT_NAME, body={}).execute()

  print 'Started training'
  pprint.pprint(start)

  import time
  # Wait for the training to complete
  while True:
    status = train.get(data=OBJECT_NAME).execute()
    pprint.pprint(status)
    if 'RUNNING' != status['trainingStatus']:
      break
    print 'Waiting for training to complete.'
    time.sleep(10)
  print 'Training is complete'

  # Now make a prediction using that training
  body = {'input': {'csvInstance': ["mucho bueno"]}}
  prediction = service.predict(body=body, data=OBJECT_NAME).execute()
  print 'The prediction is:'
  pprint.pprint(prediction)
