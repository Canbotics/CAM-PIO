import env, boto3, io, hashlib, mysql.connector
from PIL import Image, JpegImagePlugin
JpegImagePlugin._getmp = lambda x: None

print("Initializing Remote Connections")
awssession = boto3.Session(aws_access_key_id=env.AWSUSR.split("|")[1],aws_secret_access_key=env.AWSUSR.split("|")[2])
datasource = mysql.connector.connect(host=env.DBCAM.split('|')[0],user=env.DBCAM.split('|')[1],password=env.DBCAM.split('|')[2],database=env.DBCAM.split('|')[3])
sqlcursor = datasource.cursor()

print('\tSUCCESS: Connections Opened\n')

def catNewImage (a_domain = "smithy",a_origin = "/smithy/corset-form-fitting-and-shaping-top-badge.jpg",a_tags = ["test"]):
	uriPath = {'o_bucket':env.AWSS3['upload'].split("|")[0],'o_file':env.AWSS3['upload'].split("|")[1] + a_origin,'d_bucket':env.AWSS3['archive'].split("|")[0],'d_file':env.AWSS3['archive'].split("|")[1] + '/' + a_domain + '/'}
	s3r, s3c = awssession.resource('s3'), awssession.client('s3')
	bucket = s3r.Bucket(uriPath['o_bucket'])
	object = bucket.Object(uriPath['o_file'])
	objectDown, objectUp = io.BytesIO(), io.BytesIO()

	print('Retrieving {0}/{1}...'.format(uriPath['o_bucket'],uriPath['o_file']))

	object.download_fileobj(objectDown)
	print('\tSUCCESS: Image Retrieved\n')
	print('Loading Image {0}...'.format(uriPath['o_file'].rpartition('/')[2]))
	
	img = Image.open(objectDown)
	img_md5 = hashlib.md5(img.tobytes()).hexdigest().upper()
	print('\tSUCCESS: Image Loaded\n')
	print("Checking for Duplicate...")
	
	q_duplicate = "SELECT COUNT(img_id) AS img_count FROM lib_img WHERE img_md5 = '{0}'".format(img_md5)
	sqlcursor.execute(q_duplicate,())

	if (sqlcursor.fetchone()[0]):
		print("\tERROR: Duplicate Image Detected\n")
	else:
		print("\tSUCCESS: Image is Unique.\n")
		print("Inserting New Record...")
		
		img_ext = ('JPG' if img.format == 'JPEG' else img.format).lower()
		img_dim = str(img.width) + ' x ' + str(img.height)
		img_size = object.content_length
		print("\timg_md5 = {0}\n\timg_ext = {1}\n\timg_width = {2}\n\timg_height = {3}\n\timg_size = {4}\n\timg_domain = {5}".format(img_md5,img_ext,img.size[0],img.size[1],img_size,a_domain))

		q_insimg = "INSERT INTO lib_img (img_md5,img_ext,img_width,img_height,img_size,img_domain) VALUES ('{0}','{1}',{2},{3},{4},'{5}')".format(img_md5,img_ext,img.width,img.height,img_size,a_domain)
		sqlcursor.execute(q_insimg,())
		datasource.commit()
		img_id = sqlcursor.lastrowid
		
		print("\tSUCCESS: Image inserted as #{0}\n".format(img_id))
		print("Generating Thumbnail...")

		thumb = modResize (img,150,150)
		print("\tsaving : {0}/{1}{2}.thumb.{3}".format(uriPath['d_bucket'],uriPath['d_file'],img_md5,img_ext))

		thumb.save(objectUp, format=img.format)
		objectUp.seek(0)
		
		s3c.upload_fileobj(objectUp,uriPath['d_bucket'],uriPath['d_file'] + "{0}.thumb.{1}".format(img_md5,img_ext))

		print("\tSUCCESS: Thumbnail Saved\n")
		print("Moving Original File...")
		print("\tcopying {0}/{1}".format(uriPath['o_bucket'],uriPath['o_file']))

		s3r.Object(uriPath['d_bucket'],"{0}{1}.{2}".format(uriPath['d_file'],img_md5,img_ext)).copy_from(CopySource="{0}/{1}".format(uriPath['o_bucket'],uriPath['o_file']))
		print("\tdeleting {0}/{1}".format(uriPath['o_bucket'],uriPath['o_file']))

		s3r.Object(uriPath['o_bucket'],uriPath['o_file']).delete()
		print("\tSUCCESS: Image Moved\n")

	
def modResize (a_img,a_imgx,a_imgy):
	img, imgx, imgy = a_img.copy(), a_img.width, a_img.height
	
	if (a_imgx <= imgx and a_imgy <= imgy):
		if (imgx - a_imgx > imgy - a_imgy):
			img = img.resize([int(imgx * a_imgy / imgy) ,a_imgy],Image.LANCZOS)
			imgx = (img.width - a_imgx) / 2
			imgy = 0
		else:
			img = img.resize([a_imgx ,int(imgy * a_imgx / imgx)],Image.LANCZOS)
			imgx = 0
			imgy = (img.height - a_imgy) / 2
			
		img = img.crop([imgx,imgy,imgx + a_imgx,imgy + a_imgy])
	else:
		if (a_img.format == 'PNG'):
			canvas = Image.new(a_img.mode,[a_imgx,a_imgy])
		else:
			canvas = Image.new(a_img.mode,[a_imgx,a_imgy],(255,255,255))

		canvas.paste(img,[int((a_imgx - imgx) / 2),int((a_imgy - imgy) / 2)])
		img = canvas

	return(img)



	

catNewImage()




print("Closing Connections")
sqlcursor.close()
datasource.close()
print('\tSUCCESS: Connections Closed\n')




print(" =END= \n ===== ")






