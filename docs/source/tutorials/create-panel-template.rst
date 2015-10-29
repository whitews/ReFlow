Tutorial - Creating a Panel Template
====================================

.. note:: Creating a panel template requires the project-level permission "Add Project Data".  See :doc:`../permissions`

Introduction
------------

In this tutorial, we will create an example panel template containing the following parameters:

.. csv-table::
   :header: "Function", "Value Type", "Markers", "Fluorochrome"

   "Forward Scatter", "Area"
   "Side Scatter", "Area"
   "Fluorescence", "Area", "CD3", "FITC"
   "Fluorescence", "Area", "CD8", "PE-Cy7"
   "Fluorescence", "Area", "Multimer", "PE"

All the parameters specified in the panel template will be **required** to be part of the **Sample Annotation** for any uploaded FCS samples associated with this panel template. FCS samples containing *extra* parameters are allowed, and those extra parameters will be described as part of the sample annotation. However, the markers and fluorochromes in the extra channels of any uploaded sample must be added to the project's markers and fluorochromes.

If a specific parameter is not required as part of the panel for the experiment, do not include it in the panel template, else those FCS samples not meeting the panel template parameter requirements will not be able to be uploaded to the project. For example, if the FCS samples from various sites are not actually required to have a forward scatter height channel, do not include it in the panel template.

***Add more information about optional markers and fluorochromes, perhaps info about viability recommendations? Also, should we re-describe the parameter properties (function, etc.) here?***

Procedure
---------

.. important:: Prior to creating a panel template, all the markers and fluorochromes used for the parameters must have already been created. See :doc:`add-marker` and :doc:`add-fluorochrome` for instructions on creating markers and fluorochromes.

#.  Login to the ReFlow server.

#.  From the ReFlow home page, navigate to the project by clicking on the project link.

#.  From the project detail page, click the **Add Panel Template** link located under the **Panel Templates** heading.

    .. image:: ../images/project-detail.png
       :width: 1000

    .. note:: Panel templates can also be added from the **Panel Template** list page by clicking on the **Add Panel Template** button located near the upper right of that page (beside the main heading).

#.  On the panel template creation page, first give the panel template a name using the text field in the upper left-hand corner. We will call our example template "3-color Multimer".

    .. image:: ../images/create-panel-template-name.png
       :width: 1000

#.  Begin adding the parameters. We'll start by adding the forward scatter area channel by first choosing the corresponding function and value type.

    .. image:: ../images/create-panel-template-first-parameter.png
       :width: 1000

    .. note:: The red text boxes under each parameter will appear if any required information is still needed.

       - Function and value type are required for all parameters
       - Fluorescence channels must specify a marker or a fluorochrome (or both)
       - Duplicate channels are not allowed
       - The same fluorochrome cannot be in multiple channels

#.  Add a new parameter by clicking the green "Add Channel" button in the lower right.

    .. image:: ../images/create-panel-template-second-parameter.png
       :width: 1000

#.  Continue adding the remaining channels for the panel template.

    .. image:: ../images/create-panel-template-all-parameters.png
       :width: 1000

#.  Once the form is completed, click the **Sav Template** button. If there are no errors in your panel template, you will be re-directed to the panel template list.

    .. image:: ../images/create-panel-template-saved.png
       :width: 1000

    .. note:: A full stain panel variant named "FULL" is automatically created for each new panel template. Additional panel variants can also be added, see :doc:`add-panel-variant`.

.. important:: Editing a panel template is allowed as long as no Sample Annotations have been created using the template. Deleting associated Sample Annotations will enable editing the panel template, but note any existing FCS samples associated with the Sample Annotation will also be deleted.