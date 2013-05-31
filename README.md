ReFlow
======

Repository for Flow Cytometry Data

Requirements
----

* django 1.4.3
* django-guardian 1.1.0
* djangorestframework 2.2.4
* fcm 0.9.1 (https://code.google.com/p/py-fcm/)
* numpy 1.6.2
* scipy 0.11.0
* matplotlib 1.3

Optional, But Recommended Packages
__

* django-extensions 1.0.2
* django-rest-framework-docs 0.1.3
* django-debug-toolbar 0.9.4
* south 0.8.1

Installation
----

Note for Mac users: You'll need to get gfortran in addition to the command line tools (via Xcode). I recommend installing gfortran using Homebrew (http://mxcl.github.com/homebrew/)

To install fcm, you'll need to first install numpy and then scipy. To install these via pip you will need a compiler

You'll probably want to install mercurial to get the latest fcm package via:

`pip install hg+https://code.google.com/p/py-fcm/#egg=fcm`
