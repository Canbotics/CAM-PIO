import env, boto3

print("Initializing Remote Connections")

awssession = boto3.Session(aws_access_key_id=env.AWSUSR.split("|")[1],aws_secret_access_key=env.AWSUSR.split("|")[2])
print('\tSUCCESS: Connections Opened\n')

def batListFiles (a_domain = "smithy",a_origin = "/smithy",a_tags = ["test"]):
	uriPath = {'o_bucket':env.AWSS3['upload'].split("|")[0],'o_file':env.AWSS3['upload'].split("|")[1] + a_origin}
	s3r, s3c = awssession.resource('s3'), awssession.client('s3')
	bucket = s3r.Bucket(uriPath['o_bucket'] + "{0}".format(a_origin))
	
	print(uriPath)
	
	print(bucket)
	print(" +++ ")


	for object in bucket.objects.all():
		print(object)





batListFiles()












