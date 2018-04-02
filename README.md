# CAM: PIO
Canbotics Asset Manager: Python Image Organizer

> **NOTE:**
> Do **NOT** expose this to the public; this interface has no authentication or sanitization.
> Exposing publicly will create a gaping security hole.

## CLI Flags
- -a [act]
  - cat (catalogue) : Catalogue the origin file(s) in the datastore, and AWS S3 bucket defined in **env.py**
- -o [origin]
  - origin : String representing the URI (local) or key (s3) to the file.
- -d [domain]
  - domain : String representing the domain owning the image *re.[a-z]*.
- -s [source]
  - local : origin file is on local filesystem.
  - s3 : origin file is in the AWS S3 bucket, defined in **env.py**.
- -t [tags]
  - tags : Comma delimited string of tags to apply to images. type_tag-name *re.[a-z]*.









## Features
Python based app, which catalogues uploaded images:

1) Retrieve images from an **S3 bucket**.
2) Read and store pertinent information in a **MySQL database**.
3) Generate a _thumbnail_ image.
4) Save _thumbnail_ in the _Archive Folder_.
5) Copy _original_ image to the _Archive Folder_.
6) Delete _original_ image in the _Upload Folder_.



## To Do
And manipulate images:

1) Create multiple formats - as required
2) Properly name and place files (based on domain) for programmatic access

