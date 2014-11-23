Tutorial - Uploading Samples
============================

.. note:: Uploading samples requires either the project-level permission "Add Project Data" or the site-level permission "Add Site Data" for at least one site in the project.  See :doc:`../permissions`

#.  Login to the ReFlow server.

#.  From the ReFlow home page, navigate to the project by clicking on the project link.

    .. image:: ../images/project-detail.png

#.  From the project detail page, click the **Upload Samples** link to navigate to the sample upload page.

    .. image:: ../images/sample-upload-blank.png

#.  To add FCS files, either drag and drop them anywhere within the light grey region with the dashed-line border or click on the **Choose Files** button to the left of the "FCS Files" heading.

    The files should show up in **FCS Files** list. The file name is also a drop-down menu for viewing the metadata, the file's channel labels, and for removing a file from the list. The next column displays the acquisition date, which is pre-populated from the metadata if present. However, if the acquisition date field is not present in the FCS metadata, this value would need to be entered manually using the drop-down calendar menu. The last 2 columns are the channel count and file size, respectively.

    .. image:: ../images/sample-upload-new-samples.png

#.  Choose the appropriate categories from the drop-down menus on the left for the first file in the list.

    .. image:: ../images/sample-upload-pre-site-panel.png

#.  Once all the category selections have been made, click the checkbox for the first file.

    If ReFlow has previously seen a file with matching annotation for this site and panel template combination, it will automatically associate the file with that annotation. In this case, continue with the next step to add the file to the upload queue.

    However, if this is the first time this annotation set has been seen by ReFlow, a new dialog window will appear to identify all the channels present in the file. In this case, follow the instructions in :doc:`../tutorials/labelling-fcs-data`

    .. image:: ../images/sample-upload-create-site-panel.png

    .. note:: Any other files in the list that also match the categories can also be selected by clicking their checkboxes and adding the upload queue.

#.  Click the **Add to Queue** button and the file will be added to the upload queue below.

    After adding to the upload queue

    .. image:: ../images/sample-upload-file-queued.png

#.  Once all the files have been added to the upload queue, verify they have been categorized correctly **before** uploading. If a file is categorized incorrectly, click on the file name and choose **Move to File List** from the drop-down menu. This will place the file back in the FCS File List above. From there it can be re-categorized and added back to the upload queue.

    .. image:: ../images/sample-upload-file-queue-menu.png

12. Once all the files are correct, start uploading by clicking on the **Upload** button. For each file uploaded the progress bar for each file will update.

    .. image:: ../images/sample-upload-uploading.png

    And the view when all uploads are complete:

    .. image:: ../images/sample-upload-finished.png

    .. note:: ReFlow will not allow duplicate files within the same project, so if you try to re-upload duplicate files, you will see an error in the upload queue.