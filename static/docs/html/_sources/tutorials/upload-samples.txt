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

    .. note:: Any other files in the list that also match the categories can also be selected by clicking their checkboxes and adding the upload queue.

    .. image:: ../images/sample-upload-pre-site-panel.png

#.  Once all the category selections have been made, click the checkbox for the first file. If ReFlow has previously seen a file with matching annotation for the selected site within the project, it will automatically associate the file with that annotation. If this is the first time this set of annotations has been seen by ReFlow, a new dialog window will appear to identify all the channels present in the file.

    .. image:: ../images/sample-upload-create-site-panel.png

    .. note:: Skip the next step if the file annotation was recognized by ReFlow.

#.

#.  Click the **Add to Queue** button and the file will be added to the upload queue below.

    After adding to the upload queue

    .. image:: images/reflow-upload-app-categorized.png
        :width: 100%

.. raw:: pdf

    PageBreak

11. Once all 8 files from the both labs have been added to the upload queue, verify they have been categorized correctly **before** uploading. If you need to edit the categories, well, I didn't have time to implement modifying items in the upload queue, so you'll have to check the items in the upload queue and click the **Clear Selected** button. Then, re-add the file to the top section. This will be improved in the future.



12. If all the files are correct, start uploading by clicking on the **Upload** button. For each file uploaded the progress bar for each file will update.

    .. image:: images/reflow-upload-app-uploading.png
        :width: 100%

    And the view when all uploads are complete:

    .. image:: images/reflow-upload-app-finished.png
        :width: 100%

    .. note:: ReFlow will not allow duplicate files within the same project, so if you try to re-upload duplicate files, you will see an error in the upload queue.

13. Navigate back to the test project by clicking the **Home** link, then choosing the project link. Go to the **Samples** view.

.. raw:: pdf

    PageBreak

14. From the **Samples** view, click the checkboxes for both project panels in the filter, then click the **Apply** button. You should see the list update with the FCS samples you just uploaded.

    .. image:: images/reflow-samples-filter02.png
        :width: 100%

15. Show the parameters for each sample by clicking on the first icon in the row. Notice how we have mapped the FCS file's channel annotation (the PnN and PnS columns) to ReFlow's standard convention for classifying parameters (the function, markers, fluorochrome, and value type columns). This is the core concept allowing automated analysis of many files across different laboratories, regardless of the labs' FCS file annotation or the channel number used for any particular parameters.

    .. image:: images/reflow-sample-parameters.png
        :width: 100%