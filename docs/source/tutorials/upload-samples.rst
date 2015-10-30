Tutorial - Uploading Samples
============================

.. note:: Uploading samples requires either the project-level permission "Add Project Data" or the site-level permission "Add Site Data" for at least one site in the project.  See :doc:`../permissions`

#.  Login to the ReFlow server.

#.  From the ReFlow home page, navigate to the project by clicking on the project link.

#.  From the project detail page, navigate to the sample upload page by clicking the **Upload Samples** link located under the **Samples** heading.

    .. image:: ../images/project-detail.png
       :width: 1000

    .. note:: The sample upload page can also be reached from the **Sample** list page by clicking on the **Upload Samples** button located near the upper right of that page (beside the main heading).

#.  To add FCS files, either drag and drop them anywhere in the light grey region (within the dashed-line border) or click on the **Choose Files** button to the left of the "FCS Files" heading.

    .. image:: ../images/sample-upload-blank.png
       :width: 1000

    The files should show up in **FCS Files** list. The file name is displayed in the first column (which is also a drop-down menu for viewing the metadata, viewing the file's channel labels, or removing a file from the list).

    .. image:: ../images/sample-upload-new-samples.png
       :width: 1000

#.  Ensure that the acquisition date and subject are correct. These 2 fields are auto-populated in an attempt to reduce the amount of user interaction when uploading large numbers of FCS files.

    .. note:: The acquisition date is pre-populated from the metadata of each FCS file. However, if the acquisition date field is not present in the FCS metadata, this value would need to be entered manually using the drop-down calendar menu. The subject is auto-populated from the FCS file name, but should be verified by the user to make sure the correct subject code was selected.

    .. image:: ../images/sample-upload-new-samples.png
       :width: 1000

#.  For the first file in the list, choose the appropriate site and panel template from the drop-down menus on the left. At this point, an orange **Label Parameters** button will appear beside the file name of FCS samples that do not match an existing Sample Annotation for this project. For samples that do have a matching Sample Annotation, then a checkbox will be displayed.

    .. image:: ../images/sample-upload-pre-site-panel.png
       :width: 1000

#.  If a sample in the list has a **Label Parameters** button, click on it to open the sample annotation dialog window. Follow the instructions in :doc:`../tutorials/labelling-fcs-channels` to identify all the channels present in the file. Otherwise, if the file has a checkbox, then proceed to the next step.

    .. image:: ../images/sample-upload-create-site-panel.png
       :width: 1000

#.  For FCS files with a checkbox to the left of their file name (i.e. files that ReFlow has matched to a Sample Annotation), continue choosing the appropriate selections from the various drop-down menus on the left site (Panel Variant, Visit, etc.).

    .. image:: ../images/sample-upload-post-site-panel.png
       :width: 1000

#.  Once all the category selections have been made, click the checkbox for the files you wish to add to the upload queue.

    .. image:: ../images/sample-upload-file-queue-selected.png
       :width: 1000

#.  Click the **Add to Queue** button and the file will be added to the upload queue below.

    .. note:: If any of the categories have not been chosen, the **Add to Queue** button will not add the files to the queue. All the categories on the left, as well as the acquisition date and subject drop down menus, are required for all FCS files.

    .. image:: ../images/sample-upload-file-queued.png
       :width: 1000

#.  Once all the files have been added to the upload queue, verify they have been categorized correctly **before** uploading. If a file is categorized incorrectly, click on the file name and choose **Move to File List** from the drop-down menu. This will place the file back in the FCS file list above. From there it can be re-categorized and added back to the upload queue.

    .. image:: ../images/sample-upload-file-queue-menu.png

#.  Once all the files have been correctly categorized, select the files to upload by clicking their check boxes, then clicking on the **Upload Selected** button. A progress bar will be displayed showing the upload status for each file.

    .. image:: ../images/sample-upload-uploading.png

    And the view when all uploads are complete:

    .. image:: ../images/sample-upload-finished.png

    .. note:: ReFlow will not allow duplicate files within the same project, so if you try to re-upload duplicate files, you will see an error in the upload queue.