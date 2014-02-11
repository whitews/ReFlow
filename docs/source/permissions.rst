User Accounts & Permissions
===========================

ReFlow provides granular user permissions on both the project and site levels. On a project level a user can have any combination of the following permissions:

* View Project Data
* Add Project Data
* Modify/Delete Project Data
* Manage Project Users

Similarly, for **each site** within a project, a user can have the following permissions:

* View Site
* Add Site Data
* Modify/Delete Site Data
* Manage Site Users

.. note:: Sites are not shared across projects. While the same site name may be found in 2 different projects, it is purely coincidental. There is no formal relationship between those 2 sites, and user permissions are not shared between them.

Finally, there are **super-users** which have access to all projects' data as well as administrative functions of the ReFlow system. These are generally system administrators which can create new users and projects.

===================
Project Permissions
===================

-----------------
View Project Data
-----------------

A user with **View Project Data** permission for a particular project can view all data within that project, regardless of the site to which that data is associated.

----------------
Add Project Data
----------------

A user with **Add Project Data** permission for a particular project can create new data in any project category (site, subject, sample, etc.). As with the view project data permission, they can add data within any site. However, they cannot edit or remove project data.

--------------------------
Modify/Delete Project Data
--------------------------

A user with **Modify/Delete Project Data** permission for a particular project can edit and/or remove existing data in any project category (site, subject, sample, etc.). This applies for data in all a project's sites.

Modifying data within ReFlow will keep any existing relationships intact. When deleting data that has a parent relationship to other data categories, all the related data must first be deleted. For example, to delete a subject group, all subjects belonging to that subject group must be deleted first. Alternatively, those subjects could also be modified to use a different subject group, and the original subject group could be deleted.

.. warning:: Deleted data cannot be recovered as ReFlow is not meant as an archive for source data. While there is no undo operation after deleting data, the data can be re-uploaded to the project.

--------------------
Manage Project Users
--------------------

A user with **Manage Project Users** permission for a particular project can add/modify/remove users from a project. This also applies to managing the site level permissions for all users.

.. info:: A user with **Manage Project Users** permission should be treated as having all permissions, since they can technically change their own permissions within a project.

================
Site Permissions
================

---------
View Site
---------

A user with **View Site** permission for a particular site can view all data within that site. All pages will filter data accordingly, therefore a user with view permission in only one site will be unaware of FCS samples included in the same project from a different site, nor will they see the names of the other sites.

-------------
Add Site Data
-------------

A user with **Add Site Data** permission for a particular site can create new data in any site category (site panel, sample, cytometer, compensation). They cannot add new subjects or sites to the projects, nor can they modify or delete data in the site to which they have add permission.

-----------------------
Modify/Delete Site Data
-----------------------

A user with **Modify/Delete Site Data** permission for a particular site can edit and/or remove existing data in any site category (subject, sample, site panel, cytometer).

.. warning:: Deleted data cannot be recovered as ReFlow is not meant as an archive for source data. While there is no undo operation after deleting data, the data can be re-uploaded to the project.

--------------------
Manage Site Users
--------------------

A user with **Manage Site Users** permission for a particular site can add/modify/remove users from that site. They cannot manage any project-level permissions.

.. info:: A user with **Manage Site Users** permission should be treated as having all site-level permissions, since they can technically change their own permissions within that site.