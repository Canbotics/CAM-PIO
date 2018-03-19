import env, boto3, io, hashlib, mysql.connector
from PIL import Image


print("Initializing Remote Connections")
awssession = boto3.Session(aws_access_key_id=env.AWSUSR.split("|")[1],aws_secret_access_key=env.AWSUSR.split("|")[2])
datasource = mysql.connector.connect(host=env.DBCAM.split('|')[0],user=env.DBCAM.split('|')[1],password=env.DBCAM.split('|')[2],database=env.DBCAM.split('|')[3])
sqlcursor = datasource.cursor()

print('\tSUCCESS: Connections Opened\n')

def catalogue (a_domain = "smithy",a_origin = "/test/test.jpg",a_tags = ["test","something","dark side"]):
	s3 = awssession.resource('s3')
	uriPath = {
		'o_bucket':env.AWSS3['upload'].split("|")[0],
		'o_file':env.AWSS3['upload'].split("|")[1] + a_origin,
		'd_bucket':env.AWSS3['archive'].split("|")[0],
		'd_file':env.AWSS3['archive'].split("|")[1] + '/' + a_domain + '/'}
		
	
	bucket = s3.Bucket(uriPath['o_bucket'])
	object = bucket.Object(uriPath['o_file'])

	objectBytes = io.BytesIO()
	
	print('Retrieving: ' + uriPath['o_bucket'] + ' | ' + uriPath['o_file'])
	'''
	object.download_fileobj(objectBytes)
	'''
	img = Image.open("test.jpg")
	print('\tSUCCESS: Retrieved\n')
	
	print('Analyzing Image: ' + uriPath['o_file'])
	
	'''
	img = Image.open(objectBytes)
	'''
	img_md5 = hashlib.md5(img.tobytes()).hexdigest().upper()
	img_ext = ('JPG' if img.format == 'JPEG' else img.format).lower()
	img_dim = str(img.size[0]) + ' x ' + str(img.size[1])
	img_size = object.content_length
	
	print('\tMD5: {0}\n\tExtension: {1}\n\tDimensions: {2}\n\tFilesize: {3}\n\tSUCCESS: Analyzed\n'.format(img_md5,img_ext,img_dim,img_size))
	
	q_duplicate = "SELECT COUNT(img_id) AS img_count FROM lib_img WHERE img_md5 = '{0}'".format(img_md5)
	
	sqlcursor.execute(q_duplicate,())
	
	for (img_count) in sqlcursor:
		print(img_count)
	
	
	
	
	
	"""
	
	s3.Object(uriPath['d_bucket'], uriPath['d_file'] + img_md5).copy_from(CopySource = uriPath['o_bucket'] + '/' + uriPath['o_file'])
	"""
	
	

def sc_fileFormat (a_ext):
	fileFormats = {
		'jpg':'jpg',
		'jpeg':'jpg',
		'png':'png',
		'gif':'gif'
		}
	return fileFormats.get(a_ext,'extension not supported')

	
	
	
	
	"""
	
	try:
		.download_file(lv_origin,lv_temp)
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("404")
		else:
			raise
			
			
	with open(lv_temp.name) as temp:
		print(temp)
	
		with open(lv_temp.name,"wb") as temp:
	print(lv_temp)
	
			
		
			try:
				s3.Bucket(env.AWSS3['upload'].split("|")[0]).download_file(lv_origin,lv_tmp)
			except botocore.exceptions.ClientError as e:
				if e.response['Error']['Code'] == "404":
					print("404")
				else:
					raise
	"""



def testingtwo ():
	s3 = awssession.client('s3')
	s3 = awssession.resource('s3')
	
	
	for bucket in s3.buckets.all():
		print(bucket.name)


 



catalogue()




print("Closing Database")
sqlcursor.close()
datasource.close()
print('\tSUCCESS: Closed\n')




print(" ===== ")






