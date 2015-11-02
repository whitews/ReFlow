Tutorial - Labelling FCS Channels
=================================

.. note:: Labelling data is part of the FCS upload process for files with a new sample annotation. See the tutorial on uploading data for more information. :doc:`../tutorials/upload-samples`

Introduction
------------

The sample annotation dialog window for the FCS file is split into 2 main sections. The left-hand side displays the required parameters from the Panel Template (the Panel Template chosen when categorizing files in the file queue). The matching status is indicated beside each panel template parameter, where matched parameters display a check mark and non-matching parameters display a red warning symbol.

.. image:: ../images/sample-upload-create-site-panel.png
   :width: 1000

The right-hand side of the dialog displays a table list the parameters found in the FCS file. The first 3 columns display the channel labels found in the FCS file's metadata, including the channel number, the required text (PnN label), and the optional text (PnS label). The next 4 columns contain form elements used to describe the FCS channel, including the channel function, value type, and the markers/fluorochromes defined for the ReFlow project.

ReFlow pre-populates the form fields based on the contents of the PnN and PnS labels from the file's metadata. However, the auto-populated values may be incorrect or incomplete. The user must verify all the form fields to ensure the correct options have been chosen.

Procedure
---------

#.  For each parameter, choose the appropriate function and value type. Notice that the scatter and time functions will not display the marker or fluorochrome fields.

     .. note:: The "Null" function is reserved for channels that do not contain any information. This scenario would occur if a detector was left on in the cytometer even though the sample did not contain a conjugated fluorochrome intended for that channel. Do **not** use a null function for channels that contain a fluorochrome, even if those channels will not be included for analysis. If a channel contributes to the spillover matrix in any way it must be included as a fluorescence channel.

#.  For each fluorescence parameter, choose the appropriate markers and fluorochrome.

    A fluorochrome is required for fluorescence channels. If not specified you will see a warning below the channel row:

    .. image:: ../images/sample-upload-create-site-panel-fluoro-error.png
       :width: 1000

    .. note:: More than one marker is allowed for multiplex channels, though only one fluorochrome is allowed per channel. If a marker or fluorochrome is present in the FCS file, but not found in the drop-down lists, then those markers/fluorochromes must be added to the project by a user with privileges to add project data (see :doc:`../permissions`).

#.  Once all the sample's channels have been correctly described and all the panel template parameters have been matched, click on the "Save Sample Annotation" button.

    .. image:: ../images/sample-upload-create-site-panel-save.png
       :width: 1000

    .. note:: The "Save Sample Annotation" button will be disabled until all the Panel Template parameters have been matched and no error messages remain for any FCS channels.

#.  If the Sample Annotation is successfully saved, the dialog window will disappear and you can continue with the FCS file upload process (see :doc:`../tutorials/upload-samples`).