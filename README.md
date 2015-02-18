<p align="center">
<img src="insiderer.png" alt="Insiderer">
</p>

Insiderer looks inside files for metadata and hidden content

It's a webservice that start on localhost:80

Dependencies
------------

[Docvert](https://github.com/holloway/docvert-python3) is expected to be running on port 8080

Install (Debian/Ubuntu)
-----------------------

    sudo apt-get install python3 python3-magic python3-pip libmagickwand-dev python3-pdfminer
    sudo pip3 install exifread wand

Usage
-----

    python3 insiderer.py
