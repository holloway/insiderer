<p align="center">
<img src="static/insiderer.png" alt="Insiderer">
</p>

Insiderer looks inside files for metadata and hidden files and content. This metadata may include information on authorship, deleted content, and geolocation among many other pieces of information.

Unlike most other equivalent tools, Insiderer attempts to report on every file within the files you give it. Many modern formats are essentially containers for many different types of files, and so Insiderer allows you to view a hierarchy of metadata about the files you give it. For example, .docx files may contain images and those images may include authorship, geolocation, and subdocuments. Those subdocuments may have deleted content.

Insiderer may be useful to analysing your own files in order to see what metadata you are leaking to the public when you publish files onto the internet. Insiderer is free and open source, and it may be run on your own computer (bonus privacy!).

Insiderer is a work in progress. If you find a bug, or if a file doesn't work, please [report a testcase](https://github.com/holloway/insiderer/issues).

Quickstart Guide (Debian/Ubuntu)
================================

    sudo apt-get install python3 python3-magic python3-pip python3-lxml python3-gdbm libmagickwand-dev python-pdfminer python3-tk libffi-dev libssl-dev pdftk
    sudo pip3 install cherrypy pypdf2 exifread wand cython pyOpenSSL xmltodict python-dateutil python-magic mutagen
    mkdir /media/tmp

Add this line to your /etc/fstab (adjust size accordingly)

    tmpfs   /media/tmp      tmpfs   rw,nosuid,size=256m     0       0

Usage
=====

    python3 insiderer.py

    python3 insiderer.py --port=8080 --host=localhost --tmp=/tmp/

HTTPS
=====

Insiderer runs connections over SSL if there are two files found in the directory *above* named `certkey.pem` and `cert.pem`.

Recommended Dependencies
========================

[Docvert](https://github.com/holloway/docvert-python3) is expected to be running on port 8080. Without Docvert it can't process office files.


