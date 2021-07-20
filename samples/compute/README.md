# Using the Cloud Client Libraries for Python

This document demonstrates how to use the Cloud Client Libraries for Python for Compute Engine. 
It describes how to authorize requests and how to create, list, and delete instances. 
This exercise discusses how to use the `google-api-python-client` library to access Compute Engine 
resources. You can run this sample from your local machine or on a VM instance, provided that 
you have authorized the sample correctly.

For a full list of available client libraries, including other Google client libraries and 
third-party open source libraries, see the [client libraries page](https://cloud.google.com/compute/docs/api/libraries).

To view the full code example with all of the necessary imports, see the [create_instance.py file](create_instance.py).

## Objectives

 * Perform OAuth 2.0 authorization using the `oauth2client` library
 * Create, list and delete instances using the `google-api-python-client` library

## Costs

This tutorial uses billable components of Google Cloud including Compute Engine.

## Before you begin

1. In the Google Cloud Console, on the project selector page, select or create a Google Cloud project.
   [Go to project selector](https://console.cloud.google.com/projectselector2/home/dashboard).
1. Make sure that billing is enabled for your cloud project. 
   [Learn how to confirm that billing is enabled for your project.](https://cloud.google.com/billing/docs/how-to/modify-project)
1. [Install Google Cloud SDK and `gcloud`](https://cloud.google.com/sdk)
1. After the SDK is installed, run `gcloud auth application-default login`.
1. Install the [google-api-python-client](http://github.com/googleapis/google-api-python-client) library. Typically, you can run:
   
   ```bash
   pip install --upgrade google-api-python-client
   ```

1. Enable the Cloud Storage API.
   ```bash
   gcloud services enable storage.googleapis.com
   ```
1. [Create a Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets) and note the bucket name for later.

## Authorizing requests

This sample uses OAuth 2.0 authorization. There are many ways to authorize requests using OAuth 2.0,
but for the example use [application default credentials](https://developers.google.com/accounts/docs/application-default-credentials). This lets you reuse the credentials from 
the `gcloud` tool if you are running the sample on a local workstation or reuse credentials from a 
service account if you are running the sample from within Compute Engine or App Engine. You should 
have installed and authorized the `gcloud` tool in the "Before you begin" section.

Application default credentials are provided in Google API Client Libraries automatically. 
You just have to build and initialize the API:

```python
import googleapiclient
compute = googleapiclient.discovery.build('compute', 'v1')
```

See the `main()` method in the [create_instance.py](create_instance.py) script, to see how an API
client is built and used.

## Listing instances

Using `google-api-python-client`, you can list instances by using the `compute.instances().list()` method. 
You need to provide the project ID and the zone for which you want to list instances. For example:

```python
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None
```

## Adding an instance

To add an instance, use the `compute.instances().insert()` method and specify the properties of the new 
instance. These properties are specified in the request body; for details about each property see 
the [API reference for `instances.insert`](https://cloud.google.com/compute/docs/reference/latest/instances/insert).

At a minimum, your request must provide values for the following properties when you create a new 
instance:

* Instance name
* Root persistent disk
* Machine type
* Zone
* Network Interfaces

This sample starts an instance with the following properties in a zone of your choice:

* Machine type: e2-standard-2
* Root persistent disk: a new persistent disk based on the latest Debian 8 image
* The Compute Engine default service account with the following scopes:
  * https://www.googleapis.com/auth/devstorage.read_write, so the instance can read and write files in Cloud Storage
  * https://www.googleapis.com/auth/logging.write, so the instances logs can upload to Cloud Logging
* Metadata to specify commands that the instance should execute upon startup

You can see an example of instance creation in the `create_instance` method in [create_instance.py](create_instance.py) file.

### Root persistent disks

All instances must boot from a [root persistent disk](https://cloud.google.com/compute/docs/disks/create-root-persistent-disks).
The root persistent disk contains all of the necessary files required for starting an instance. 
When you create a root persistent disk you must select a public image or a custom image to apply to 
the disk. In the example above, a new root persistent disk is created based on Debian 8 at the same 
time as the instance. However, it is also possible to create a disk beforehand and attach it to the 
instance.

To create an instance using your own custom OS image, you need to provide a different URL than 
the one included in the example. For more information about starting an instance with your own 
images, see [Creating an instance from a custom image](https://cloud.google.com/compute/docs/instances/create-start-instance#creating_an_instance_from_a_custom_image).



### Instance metadata

When you create your instance, you might want to include instance metadata such as a [startup script](https://cloud.google.com/compute/docs/startupscript), 
configuration variables, and SSH keys. In the example above, you used the `metadata` field in your 
request body to specify a startup script for the instance and some configuration variables as 
key/values pairs. The [startup-script.sh](startup-script.sh) shows how to read these variables and use them 
to apply text to an image and upload it to [Cloud Storage](https://cloud.google.com/storage).

## Deleting an Instance

To delete an instance, you need to call the `compute.instances().delete()` method and provide the name, 
zone, and project ID of the instance to delete. When the `autoDelete` parameter is set to `true` for the 
boot disk it is also deleted with the instance. This setting is off by default but is 
useful when your use case calls for disks and instances to be deleted together.

```python
def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()
```

## Running the sample

You can run the full sample by downloading the code and running it on the command line. Make sure 
to download the `create_instance.py` file and the `startup-script.sh` file. To run the sample:

```bash
python create_instance.py --name [INSTANCE_NAME] --zone [ZONE] [PROJECT_ID] [CLOUD_STORAGE_BUCKET]
```

where:

* `[INSTANCE_NAME]` is the name of the instance to create.
* `[ZONE]` is the desired zone for this request.
* `[PROJECT_ID]` is our project ID.
* `[CLOUD_STORAGE_BUCKET]` is the name of the bucket you initially set up but without the `gs://` prefix.

For example:

```bash
python python-example.py --name example-instance --zone us-central1-a example-project my-gcs-bucket
```

## Waiting for operations to complete

Requests to the Compute Engine API that modify resources such as instances immediately return a 
response acknowledging your request. The acknowledgement lets you check the status of the requested 
operation. Operations can take a few minutes to complete, so it's often easier to wait for the 
operation to complete before continuing. This helper method waits until the operation completes 
before returning:

```python
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
```

When you query per-zone operations, use the `compute.zoneOperations.get()` method. When you query global 
operations, use the `compute.globalOperations.get()` method. For more information, see zone resources.

## Cleaning up

To avoid incurring charges to your Google Cloud account for the resources used in this tutorial, 
either delete the project that contains the resources, or keep the project and delete the 
individual resources.

### Delete your Cloud Storage bucket

To delete a Cloud Storage bucket:
1. In the Cloud Console, go to the Cloud Storage [Browser page](https://console.cloud.google.com/storage/browser).
1. Click the checkbox for the bucket that you want to delete.
1. To delete the bucket, click `Delete`, and then follow the instructions.
