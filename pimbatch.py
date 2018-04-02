

def batListFiles (a_domain,a_batch):
	print("Loading Batch File ({0})".format(a_batch))
	
	batchList  = open(a_batch,'r')
	print('\tSUCCESS: File Opened\n')
	
	for img in batchList:
		tags = img.split(';')[1].split('.')[0]
		origin = img.split('\n')[0]
		print("python pim.py -d {0} -a cat -o {1} -t {2}".format(a_domain,origin,tags))








batListFiles('smithy','batch.txt')
