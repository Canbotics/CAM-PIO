import os, sys, getopt, env, boto3, io, hashlib, mysql.connector, re
from PIL import Image, JpegImagePlugin
JpegImagePlugin._getmp = lambda x: None
	
def getLocal (origin):
	print("GET image from LOCAL")
	return (Image.open(origin), os.path.getsize(origin))

def getRemote (domain,origin):
	print("GET image from AWS S3")
	awssession = boto3.Session(aws_access_key_id=env.AWSUSR.split("|")[1],aws_secret_access_key=env.AWSUSR.split("|")[2])
	s3r = awssession.resource('s3')
	
	bucket = s3r.Bucket(env.S3BUCKET)
	objdown = bucket.Object('upload/{0}/{1}'.format(domain,origin))
	img = io.BytesIO()
	
	objdown.download_fileobj(img)
	return (Image.open(img), objdown.content_length)
	
def putRemote (img,format,destination):
	awssession = boto3.Session(aws_access_key_id=env.AWSUSR.split("|")[1],aws_secret_access_key=env.AWSUSR.split("|")[2])
	s3c = awssession.client('s3')

	objup = io.BytesIO()
	img.save(objup,format=format)
	objup.seek(0)

	s3c.upload_fileobj(objup,env.S3BUCKET,destination)

def delLocal (origin):
	os.remove(origin)
	
def delRemote (domain,origin):
	awssession = boto3.Session(aws_access_key_id=env.AWSUSR.split("|")[1],aws_secret_access_key=env.AWSUSR.split("|")[2])
	s3r = awssession.resource('s3')

	s3r.Object(env.S3BUCKET,'upload/{0}/{1}'.format(domain,origin)).delete()
	


def modResize (obj,tarx,tary):
	print("MOD resize")
	img, imgx, imgy = obj.copy(), obj.width, obj.height
	print("\tfrom {0}x{1} to {2}x{3}".format(imgx,imgy,tarx,tary))
	
	if (tarx <= imgx and tary <= imgy):
		if (imgx - tarx > imgy - tary):
			img = img.resize([int(imgx * tary / imgy) ,tary],Image.LANCZOS)
			imgx, imgy = (img.width - tarx) / 2, 0
		else:
			img = img.resize([tarx ,int(imgy * tarx / imgx)],Image.LANCZOS)
			imgx, imgy = 0, (img.height - tary) / 2
			
		img = img.crop([imgx,imgy,imgx + tarx,imgy + tary])
	else:
		if (obj.format == 'PNG'):
			canvas = Image.new(obj.mode,[tarx,tary])
		else:
			canvas = Image.new(obj.mode,[tarx,tary],(255,255,255))

		canvas.paste(img,[int((tarx - imgx) / 2),int((tary - imgy) / 2)])
		img = canvas

	print("\tSUCCESS\n")
	return(img)
	
	
def catImageNew (domain,source,origin,tags):
	print("CAT image new")
	if (source == 's3'):
		img, img_size = getRemote(domain,origin)
	else:
		img, img_size = getLocal(origin)
		
	img_md5 = hashlib.md5(img.tobytes()).hexdigest().upper()
	print("\tMD5: {0}\n\tSUCCESS\n".format(img_md5))

	print("\tOPEN connection")
	datasource = mysql.connector.connect(host=env.DBCAM.split('|')[0],user=env.DBCAM.split('|')[1],password=env.DBCAM.split('|')[2],database=env.DBCAM.split('|')[3])
	sqlcursor = datasource.cursor()
	sqlcursor.execute("SELECT COUNT(img_id) FROM lib_img WHERE img_md5 = '{0}'".format(img_md5),())
	print("\tSUCCESS\n")

	if (sqlcursor.fetchone()[0]):
		print("\n\n! ERROR: Duplicate Image Detected\n! ERROR: EXITING")
		return False, img_md5
	else:
		img_ext, img_x, img_y = ('JPG' if img.format == 'JPEG' else img.format).lower(), img.width, img.height
		
		print("\tINSERT image into database")
		sqlcursor.execute("INSERT INTO lib_img (img_md5,img_ext,img_width,img_height,img_size,img_domain) VALUES ('{0}','{1}',{2},{3},{4},'{5}')".format(img_md5,img_ext,img.width,img.height,img_size,domain),())
		datasource.commit()
		img_id = sqlcursor.lastrowid
		print("\tSUCCESS\n")

		thumb = modResize(img,150,150)
		
		print("\tUPLOAD image into AWS S3 archive")
		putRemote(thumb,img.format,'archive/{0}/{1}.thumb.{2}'.format(domain,img_md5,img_ext))
		putRemote(img,img.format,'archive/{0}/{1}.{2}'.format(domain,img_md5,img_ext))
		print("\tSUCCESS\n")
		
		print("\tDELETE original file")
		if (source == 's3'):
			delRemote(domain,origin)
		else:
			delLocal(origin)
		print("\tSUCCESS\n")

		catImageTag(img_id,tags)

	sqlcursor.close()
	datasource.close()

def catImageTag (img_id,tags):
	print("CAT image tag")
	print("\t{0}".format(tags))
	
	for tag in tags:
		print("\t{0}:".format(tag))
		tag_class, tag_name = tag.split('_')[0],tag.split('_')[1]

		datasource = mysql.connector.connect(host=env.DBCAM.split('|')[0],user=env.DBCAM.split('|')[1],password=env.DBCAM.split('|')[2],database=env.DBCAM.split('|')[3])
		sqlcursor = datasource.cursor()
		
		sqlcursor.execute("SELECT tag_id FROM lib_tag WHERE tag_class = '{0}' AND tag_name = '{1}'".format(tag_class, tag_name),())
		rs_tagid = sqlcursor.fetchone()
		tag_id = (0 if (rs_tagid is None) else rs_tagid[0])
		
		print("\t\tid: {0}".format(tag_id))
		
		if (not tag_id):
			print("\t\tINSERT tag {0}".format(tag))
			sqlcursor.execute("INSERT INTO lib_tag (tag_class,tag_name) VALUES ('{0}','{1}')".format(tag_class, tag_name),())
			datasource.commit()
			tag_id = sqlcursor.lastrowid
			print("\t\tid: {0}".format(tag_id))
		
		sqlcursor.execute("SELECT COUNT(xref_id) FROM xref_img_tag WHERE img_id = '{0}' AND tag_id = '{1}'".format(img_id,tag_id),())
		rs_xref = sqlcursor.fetchone()
		xref_id = (0 if (rs_xref is None) else rs_xref[0])
		print("\t\txref id: {0}".format(xref_id))
		
		if (not xref_id):
			print("\t\tINSERT xref {0}-{1}".format(img_id,tag_id))
			sqlcursor.execute("INSERT INTO xref_img_tag (img_id,tag_id) VALUES ({0},{1})".format(img_id, tag_id),())
			datasource.commit()
			xref_id = sqlcursor.lastrowid
			print("\t\txref id: {0}".format(tag_id))

		print("\t\tSUCCESS\n")
	


def batImageNew (domain,source,origin):
	print("BAT image new")
	
	if (source == "local"):
		files = [file for file in os.listdir(origin) if (os.path.isfile(os.path.join(origin,file)))]
		print("\tBATCH PROCESSING : {0}\n".format(files))
		
		for file in files:
			img = os.path.join(origin,file)
			if (re.search('^[^\.]+\.[^\.]+\.[^\.]+$',file)):
				tags = re.sub('[^a-z0-9_,-]','',file.split('.')[1].lower()).split(',')
			else:
				tags = []
				
			print("-a new\n-d {0}\n-o {1}\n-t {2}".format(domain,img,tags))
			print("++++++++++\n\n".format(file,tags))
			catImageNew(domain,source,img,tags)
			print("\n==========\n\n".format(file,tags))
		






	
def appRun (a_args):
	origin, act, tags, domain, source = '','',[],'smithy','local'
	
	try:
		opts, args = getopt.getopt(a_args,"d:o:a:t:s:")
	except getopt.GetoptError:
		print ("ERROR: Invalid flags")
		sys.exit(2)
		
	for opt, arg in opts:
		if (opt == '-o'):
			origin = arg
		elif (opt == '-d'):
			domain = re.sub('[^a-z0-9_-]','',arg.lower())
		elif (opt == '-a'):
			act = arg
		elif (opt == '-t'):
			tags = re.sub('[^a-z0-9_,-]','',arg.lower()).split(',')
		elif (opt == '-s'):
			source = 's3' if arg.lower() == 's3' else 'local'
	
	if (act == 'new'):
		catImageNew(domain,source,origin,tags)
	elif (act == 'batnew'):
		batImageNew(domain,source,origin)
	
appRun(sys.argv[1:])