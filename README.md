# CAM-PIO
Canbotics Asset Manager: Python Image Organizer

> **NOTE**
> Do **NOT** expose this to the public; this interface has no authentication or sanitization.
> Exposing publicly will create a gaping security hole.

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

