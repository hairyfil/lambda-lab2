import boto3
from werkzeug import secure_filename
from wand.image import Image
import json
import os


s3 = boto3.client('s3')


def lambda_handler(event, context):
    bucketname=(event["Records"][0]["s3"]["bucket"]["name"])
    key= (event["Records"][0]["s3"]["object"]["key"])
    
    print(event["Records"][0]["s3"]["bucket"]["name"])
    print ("my incoming bucketname = ", bucketname)
    print ("my incoming key = ", key)

    input_filename = secure_filename(key)
    output_filename = key.rsplit(".",1)[0] + "-transformed.jpg"

    print("my secure input_filename = ", input_filename)
    print("my output_filename = ", output_filename)

    with open('/tmp/image.jpg', 'wb') as data:
        s3.download_fileobj(bucketname, key, data)

    with Image(filename='/tmp/image.jpg') as left:
        print('width =', left.width)
        print('height =', left.height)
        #img.resize(200, 200)
        with left.clone() as right:
            right.spread(8.0)
            left.extent(width=left.width*2)
            left.composite(right, top=0, left=right.width)
        #this will save the resized file
        left.save(filename='/tmp/image.jpg')


    upload = boto3.resource('s3')
    uploadbucketname = bucketname+"-transformed"


    print("my uploadbucketname = ", uploadbucketname)
    print("my output filename = ", output_filename)
    print("uploading the resized image...")
    
    try:
        upload.Object(uploadbucketname, output_filename).upload_file('/tmp/image.jpg')
        print("uploading succeeded")
    except Exception as e:
        print ("uploading failed")
        print ("%s", e)
    