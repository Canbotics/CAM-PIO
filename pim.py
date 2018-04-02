import os, sys, getopt, env, boto3, io, hashlib, mysql.connector, re
from PIL import Image, JpegImagePlugin
JpegImagePlugin._getmp = lambda x: None
	
def getLocal (origin):
	return (Image.open(origin), os.path.getsize(origin))

def getRemote (domain,origin):
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
	img, imgx, imgy = obj.copy(), obj.width, obj.height
	
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

	return(img)
	
	
def catNewImage (domain,source,origin,tags):
	if (source == 's3'):
		img, img_size = getRemote(domain,origin)
	else:
		img, img_size = getLocal(origin)
		
	img_md5 = hashlib.md5(img.tobytes()).hexdigest().upper()

	datasource = mysql.connector.connect(host=env.DBCAM.split('|')[0],user=env.DBCAM.split('|')[1],password=env.DBCAM.split('|')[2],database=env.DBCAM.split('|')[3])
	sqlcursor = datasource.cursor()

	sqlcursor.execute("SELECT COUNT(img_id) FROM lib_img WHERE img_md5 = '{0}'".format(img_md5),())

	if (sqlcursor.fetchone()[0]):
		print("ERROR: Duplicate Image Detected\n")
		return False, img_md5
	else:
		img_ext, img_x, img_y = ('JPG' if img.format == 'JPEG' else img.format).lower(), img.width, img.height

		sqlcursor.execute("INSERT INTO lib_img (img_md5,img_ext,img_width,img_height,img_size,img_domain) VALUES ('{0}','{1}',{2},{3},{4},'{5}')".format(img_md5,img_ext,img.width,img.height,img_size,domain),())
		datasource.commit()
		img_id = sqlcursor.lastrowid
		
		thumb = modResize(img,150,150)
		
		putRemote(thumb,img.format,'archive/{0}/{1}.thumb.{2}'.format(domain,img_md5,img_ext))
		putRemote(img,img.format,'archive/{0}/{1}.{2}'.format(domain,img_md5,img_ext))
		
		if (source == 's3'):
			delRemote(domain,origin)
		else:
			delLocal(origin)

	

	
	
	
		'''

		def catTagImage (a_id,a_tags=["product_gladius","subcat_sword","section_design","category_melee","segment_weapon"]):
			print("\tTags: {0}".format(a_tags))
			
			for tag in a_tags:
				print("\tTag: {0}".format(tag))
				
				q_duplicate = "SELECT tag_id FROM lib_tag WHERE tag_name = '{0}' AND tag_class = '{1}'".format(tag.split('_')[1],tag.split('_')[0])
				sqlcursor.execute(q_duplicate,())
				rs_tagid = sqlcursor.fetchone()
				
				if (rs_tagid):
					tag_id = rs_tagid[0]
					print("\t\ttag id #{0}".format(tag_id))
				else:
					print("\t\tadding tag...")
					
					q_instag = "INSERT INTO lib_tag (tag_name,tag_class) VALUES ('{0}','{1}')".format(tag.split('_')[1],tag.split('_')[0])
					sqlcursor.execute(q_instag,())
					datasource.commit()
					tag_id = sqlcursor.lastrowid
					print("\t\t\ttag id #{0}".format(tag_id))
				
				q_duplicate = "SELECT COUNT(xref_id) FROM xref_img_tag WHERE img_id = '{0}' AND tag_id = '{1}'".format(a_id,tag_id)
				sqlcursor.execute(q_duplicate,())
				rs_xref = sqlcursor.fetchone()[0]
				
				if (not rs_xref):
					print("\t\ttagging image.")
					q_insxref = "INSERT INTO xref_img_tag (img_id, tag_id) VALUES ({0},{1})".format(a_id,tag_id)
					sqlcursor.execute(q_insxref,())
					datasource.commit()
					print("\t\tSUCCESS: Tag Added")
				else:
					print("\t\tERROR: Image Already Tagged.")




			
		catTagImage(1)

		'''	


	


		catTagImage(img_id,a_tags)

	sqlcursor.close()
	datasource.close()











	
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
			domain = re.sub(r'[^a-z0-9_-]','',arg.lower())
		elif (opt == '-a'):
			act = arg
		elif (opt == '-t'):
			tags = re.sub(r'[^a-z0-9_,-]','',arg.lower()).split(',')
		elif (opt == '-s'):
			source = 's3' if arg.lower() == 's3' else 'local'
	
	if (act == 'cat'):
		catNewImage(domain,source,origin,tags)
	
appRun(sys.argv[1:])