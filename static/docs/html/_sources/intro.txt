Introduction
============

===============
What is ReFlow?
===============

ReFlow is a web-based repository for flow cytometry data (i.e.
FCS files), with a primary focus on reproducible automated analysis. While
other online repositories exist for flow cytometry data, most are focused on
data sharing under a software as a service (SaaS) model. ReFlow is not a
solitary SaaS application, and is meant to be deployed within an organization,
institution, or laboratory.

ReFlow is open source software released under a BSD-style license and developed
at Duke University in the Department of Biostatistics & Bioinformatics.

=====================
Why was ReFlow built?
=====================

ReFlow was developed to solve the problem of inconsistent data annotation to
drive automated analysis pipelines.

Flow cytometry data is complex and requires extensive training and expertise
to analyze. Even with substantial experience in the field,
manual analysis is subject to inter-operator variability,
especially when attempting to find rare cell subsets. As a result,
it is difficult to harmonize assays and interpret results across institutions.
Automated analysis of flow cytometry data across different laboratories
would provide a more objective basis for the identification of these cell subsets.

However, when implementing the automated analysis pipeline,
problems arose in identifying the individual channels within the flow
cytometry data files. The Flow Cytometry Standard (FCS) defines which
metadata fields contain channel information but not how individual
channels must be labelled. As a result, annotation varies across AND within
laboratories. For example, one FCS file may contain a channel labelled "CD14
PB vAmine" whereas another FCS file with the same "panel" may be labelled
"CD14 PacBlue violetAmine" and another may just contain "Violet-A".
Further, these parameters may be in different channel numbers.

==============
Major Features
==============

* Supports FCS data files
* Data is organized into different projects
* Each project can have multiple sites/labs
* Project metadata (subject codes, fluorochromes, etc) customized per project
* User permissions can be defined for each project
* FCS parameters are coerced into a common project namespace
* All FCS metadata can be viewed from a web browser with no software to install
* Compensation matrices can be uploaded/edited on the server
* Prevents duplicate files from being uploaded to the same project
* Allows filtering FCS samples by multiple criteria
* Robust and feature complete REST API for programmatically accessing data

=================
ReFlow Data Types
=================

=======================  ===========
Name                     Description
=======================  ===========
Project                  Sequesters data for an experiment from other experiments in the system. This is the top level of the ReFlow hierarchy.
Marker                   Flow cytometry marker (e.g. CD3, IFNg).
Fluorochrome             Flow cytometry fluorochrome (e.g. FITC, AquaAmine)
Subject                  The individual from which the biological specimen was taken. A subject may optionally belong to a subject group.
Subject Group            Categorizes subjects into groups, useful for differentiating a “normal” from a “control”, etc.
Site                     The location where an FCS file was produced, such as a laboratory name, institution, etc.
Visit Type               Categorizes samples into temporal groups, such as “Send out 3” for a proficiency test project or “Baseline” for a clinical trial project. Note this is not the same as the FCS acquisition date.
Stimulation              In vitro conditions used to prepare cells from which an FCS file was produced.
Sample                   An FCS file.
Panel Template           A collection of flow cytometry parameters used as a master template for a specific panel. Any parameters listed in a Panel Template must be present in uploaded files associated with that template.
Sample Annotation        A specific implementation of a panel template used to map FCS parameters from a site to a project's Panel Template.
Compensation             A compensation matrix that can optionally be associated with one or more Samples.
=======================  ===========

