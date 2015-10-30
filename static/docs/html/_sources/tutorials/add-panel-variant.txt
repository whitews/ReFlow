Tutorial - Adding a Panel Variant
=================================

.. note:: Creating a panel template requires the project-level permission "Add Project Data".  See :doc:`../permissions`

Introduction
------------

This tutorial will followup on the example used in :doc:`create-panel-template` to create an fluorescence minus one (FMO) panel variant for the CD3 FITC parameter. The full stain panel from that example contained the following parameters:

.. csv-table::
   :header: "Function", "Value Type", "Markers", "Fluorochrome"

   "Forward Scatter", "Area"
   "Side Scatter", "Area"
   "Fluorescence", "Area", "CD3", "FITC"
   "Fluorescence", "Area", "CD8", "PE-Cy7"
   "Fluorescence", "Area", "Multimer", "PE"

Panel variants are a "tagging" mechanism to differentiate the variations commonly used in flow cytometry panels. Since panel variants share the same channel structure (even if the actual fluorochromes are not present, or are not conjugated to the same antibody), there is no need to create new panel templates to describe them. ReFlow provides options for the following panel variant types:

- Full stain
- FMO
- Isotype control
- Unstained

Procedure
---------

#.  Login to the ReFlow server.

#.  From the ReFlow home page, navigate to the project by clicking on the project link.

#.  From the project detail page, navigate to the panel template list by clicking on the **View Panel Templates** located under the **Panel Templates** heading.

#.  On the panel template list, click the plus sign in the Panel Variants column in the row of the panel template for which you want to create a new panel variant.

    .. image:: ../images/create-panel-template-saved.png
       :width: 1000

#.  Choose a panel variant from the list. In our example we will choose fluorescence minus one.

    .. image:: ../images/choose-panel-variant-type.png
       :width: 1000

#.  Enter the parameter(s) that has varied from the full stain panel in the **Parameter(s)** text box. In our example we are creating an FMO variant for the FITC parameter.

    .. image:: ../images/choose-panel-variant-parameter.png
       :width: 1000

#.  Once the form is completed, click the **Save** button.

#.  Once the new marker is created, the modal window will close and the new panel variant will be displayed as a green tag with a label combining the panel variant abbreviation with the parameter chosen.

    .. image:: ../images/panel-template-new-variant.png
       :width: 1000