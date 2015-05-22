Site Navigation
===============

============
Login Screen
============

Login to the ReFlow server using the web address and user credentials provided by the ReFlow system administrator.

.. image:: images/login.png

=========
Home Page
=========

The home page is a dashboard view of all the projects to which you belong as well as the user permissions you have for each project. You will not see any projects to which you do not have view permissions. In the upper right corner of the page you will find your username and a 'Logout' link to log out of the system. Note the 'Documentation' link to access general ReFlow usage documentation. ReFlow administrators will have an additional 'Admin' link to manage administrative tasks such as adding new markers, fluorochromes, etc.

.. image:: images/home.png
   :width: 1000

==============
Project Detail
==============

The project detail page is a dashboard view with links to all data categories within a project. Some categories are related to others, for example, a particular cytometer belongs to a particular site. Note the "breadcrumb" path directly below the ReFlow logo. This area displays your current browsing location, with links to that location's parent pages. There are also links for the most common actions under each data category.

.. image:: images/project-detail.png

.. note:: Some pages within ReFlow will be displayed slightly different depending on user permissions. For example, on the project home page, users with "Manage users" permission for that project will see a "Manage Users" link to the right of the project name. Likewise, users with "Edit project" permission for that project will see an "Edit Project" link.

A non-admin user would see the project detail view as:

.. image:: images/project-detail-non-admin-user.png

:doc:`tutorials/add-project`

================================
Project Category - Subject Group
================================

Subject groups are simply a way to group subjects. There are no rules governing what the subject group represents and the subject group name can be any text string. However, duplicate subject group names are not allowed within a project.

:doc:`tutorials/add-subject-group`

==========================
Project Category - Subject
==========================

A subject represents an individual from which a specimen is taken to create an FCS sample. A subject code is required. Subjects may optionally belong to a subject group. A subject can also be marked as a batch control, a field used in the automated analysis pipeline.

:doc:`tutorials/add-subject`

=======================
Project Category - Site
=======================

Sites are locations at which FCS samples are created. There are no rules governing what the site represents, it could be an institution or a particular laboratory. The site name can be any text string. However, duplicate site names within a Project are not allowed.

There are also site-level permissions which restrict access for site users. Users with access to one site within a project will not have access to data in other sites within the project. See :doc:`../permissions` for more information.

.. note:: Sites are not shared across projects. While the same site name may be used in 2 different projects, it is purely coincidental. There is no formal relationship between sites with the same name across different projects, and user permissions are not shared between them.

:doc:`tutorials/add-site`

============================
Project Category - Cytometer
============================

Cytometers represent specific flow cytometers used to acquire FCS samples. A cytometer must belong to a pre-defined site, and the cytometer name and serial number fields are required. A cytometer name must be unique within a site.

:doc:`tutorials/add-cytometer`

=============================
Project Category - Visit Type
=============================

Visit types can represent any temporal separation of data acquisition within a project. For clinical trials, a visit type may represent subject time points such as a baseline or 3 month follow-up. For proficiency tests, a visit type may represent a specific send out. The visit type name is required and must be unique within a project. The description is optional.

:doc:`tutorials/add-visit-type`

==============================
Project Category - Stimulation
==============================

A stimulation represents the use of a stimulant on a specimen prior to acquiring the FCS sample in order to evaluate activation of cell subsets in intracellular staining (ICS) or proliferation assays. Typically, the stimulant is a pathogen- or cancer-specific mixture of antigenic peptides designed to bind to and activate antigen-specific cells, but non-specific stimulants such as the SEB super antigen may also be used as positive controls.

The stimulation name is required and must be unique within a project. The description is optional. Since the stimulation category is required for uploaded samples, non-stimulated conditions can be represented by any text string such as "Unstimulated", "No stim", or any other preferred text string.

:doc:`tutorials/add-stimulation`

======================
Non-project Categories
======================

Several categories within ReFlow are not defined within projects and their values are shared across all projects. These include:

* Specimens
* Markers
* Fluorochromes
* Workers

To view or modify data for these categories requires superuser privileges. To navigate to the non-project category views, click on the **Admin** link in the upper right (only available for superusers).

.. image:: images/admin-view.png

Specimens
---------

A specimen represents a type of biological tissue from which an FCS sample was acquired. There are several specimens included by default in ReFlow, but the list may be modified when deploying a ReFlow server. The default list includes:

====  ===========
Name  Description
====  ===========
BAL   Bronchoalveolar Lavage
BM    Bone Marrow
LNC	  Lymph Node Cells
PBMC  Peripheral Blood Mononuclear Cells
WB    Whole Blood
====  ===========

Markers
-------

A marker is a property of a cell that can be used to discriminate cell subsets, such as a cell surface or intracellular protein. Typically, one or more markers are utilized in flow cytometry to identify a specific cell population.

Fluorochromes
-------------

A fluorochrome represents a specific fluorescent chemical. Fluorochromes are typically conjugated to a marker.