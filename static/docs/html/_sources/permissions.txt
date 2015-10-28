User Accounts & Permissions
===========================

ReFlow provides granular user permissions on both the project and site levels. On a project level a user can have any combination of the following permissions:

* View Project Data
* Add Project Data
* Modify Project Data
* Manage Project Users
* Submit Process Requests

Similarly, for **each site** within a project, a user can have the following permissions:

* View Site Data
* Add Site Data
* Modify Site Data

.. note:: Sites are not shared across projects. While the same site name may be found in 2 different projects, it is purely coincidental. There is no formal relationship between those 2 sites, and user permissions are not shared between them.

Finally, there are **super-users**, which have access to all projects' data as well as administrative functions of the ReFlow system. These are generally system administrators that can create new users and projects.

===================
Project Permissions
===================

-----------------
View Project Data
-----------------

A user with **View Project Data** permission for a particular project can view all data within that project, including data for all sites. This permission does not allow a user to add new data or modify existing data.

----------------
Add Project Data
----------------

A user with **Add Project Data** permission for a particular project can create new data in any project category (site, subject, sample, etc.), including uploading FCS files for any site. However, they cannot edit or remove project data.

-------------------
Modify Project Data
-------------------

A user with **Modify Project Data** permission for a particular project can edit or remove existing data in any project category (site, subject, sample, etc.). This applies to data in all a project's sites.

Modifying data within ReFlow will keep existing relationships intact. For example, if you edit a subject group name, all existing subjects under that subject group will remain associated to the modified subject group and will display the updated subject group information.

When deleting data that has related children, all the related data will also be deleted. ReFlow will display a confirmation dialog window informing the user that other data will be deleted. For example, deleting a subject group will also delete all subjects and FCS samples belonging to that subject group. To keep those related subjects, a user could modify them to refer to a different subject group, and then the original subject group could be deleted.

.. warning:: Deleted data cannot be recovered as ReFlow is not meant as an archive for source data. While there is no undo operation after deleting data, the data can be re-uploaded to the project.

--------------------
Manage Project Users
--------------------

A user with **Manage Project Users** permission for a particular project can add and remove users from a project, as well as modify user permissions for users belonging to the project. This also applies to managing the site level permissions for all users.

.. important:: A user with **Manage Project Users** permission should be treated as having all permissions, since they can technically change their own permissions within a project.

-----------------------
Submit Process Requests
-----------------------

A user with **Submit Process Requests** permission can submit new process requests to the automated analysis pipeline.


================
Site Permissions
================

---------
View Site
---------

A user with **View Site** permission for a particular site can view all data within that site. All pages will filter data accordingly. Therefore, a user with view permission in only one site will be unaware of FCS samples included in the same project from a different site, nor will they see the names of the other sites. This permission does not allow the user to add or modify site data to the site.

-------------
Add Site Data
-------------

A user with **Add Site Data** permission for a particular site can create new data in any site category (sample annotation, sample, and compensation). They cannot add new subjects or sites to the project, nor can they modify or delete data in the site to which they have add permission.

----------------
Modify Site Data
----------------

A user with **Modify Site Data** permission for a particular site can edit and/or remove existing data in any site category (sample annotation, sample, and compensation).

.. warning:: Deleted data cannot be recovered as ReFlow is not meant as an archive for source data. While there is no undo operation after deleting data, the data can be re-uploaded to the project.
