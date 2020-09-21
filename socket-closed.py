from googleapiclient import discovery
import httplib2


with discovery.build("drive", "v3") as client:
    pass