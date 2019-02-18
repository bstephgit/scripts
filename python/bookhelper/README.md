## Bookhelper package

Bookhelper initialize the upload page of the bookstore site with data comming from sites. 
It use selenium package to instantiate browser and fill page form with title, author,
publication year and description. 

See pip_req.txt to see which packege needs to be installed as dependency.

the book helper needs url link file as input to download relevant book 
information from the site.

A script, 'links.cmd', helps starting all the python package.
Commnd is:

links.cmd <url link file> [TYPES]
TYPES can be pdf, epub, chm, mobi, azw3
additional information can be added: 
- zip or rar if file is in archive.
- code if the archive contains code examples.

REMARK: link.cmd only works for windows.
