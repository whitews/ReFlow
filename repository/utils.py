from django.utils import simplejson
import re

from repository.models import *


def apply_panel_to_sample(panel, sample):
    """
    Creates SampleParameterMap instances for provided Sample matching the Parameters in the provided Panel.
    Note that the panel and sample provided must have the same parent site and
    the sample must not have any existing SampleParameterMap relations.

    Returns 0 status if successful

    sample - The Sample instance for which the SampleParameterMaps will be created
    panel - The Panel instance providing the parameters to apply to the sample
    """

    if sample.sampleparametermap_set.count() != 0:
        return 1

    errors = []
    sample_parameters = {}  # parameter_number: PnN text
    sample_param_count = 0

    # Validate that it is a site panel
    if panel.site == sample.site:

        # Read the FCS text segment and get the number of parameters
        sample_text_segment = sample.get_fcs_text_segment()

        if 'par' in sample_text_segment:
            if sample_text_segment['par'].isdigit():
                sample_param_count = int(sample_text_segment['par'])
            else:
                errors.append("Sample reports non-numeric parameter count")
        else:
            errors.append("No parameters found in sample")

        # Get our parameter numbers from all the PnN matches
        for key in sample_text_segment:
            matches = re.search('^P(\d+)N$', key, flags=re.IGNORECASE)
            if matches:
                # while we're here, verify sample parameter PnN text matches a parameter in selected panel
                if panel.panelparametermap_set.filter(fcs_text=sample_text_segment[key]):
                    sample_parameters[matches.group(1)] = sample_text_segment[key]
                else:
                    errors.append(
                        "Sample parameter " +
                        sample_text_segment[key] +
                        " does not match a parameter in selected panel")

        # Verify:
        # sample parameter count == sample_param_count == selected panel parameter counts
        if len(sample_parameters) == sample_param_count == len(panel.panelparametermap_set.all()):

            # Copy all the parameters from PanelParameterMap to SampleParameterMap
            for key in sample_parameters:
                ppm = panel.panelparametermap_set.get(fcs_text=sample_parameters[key])

                # Finally, construct and save our sample parameter map for all the matching parameters
                spm = SampleParameterMap()
                spm.sample = sample
                spm.parameter = ppm.parameter
                spm.value_type = ppm.value_type
                spm.fcs_number = key
                spm.fcs_text = sample_parameters[key]
                spm.save()
        else:
            errors.append("Matching parameter counts differ between sample and selected panel")

        # If something isn't right, return errors
        if len(errors) > 0:
            json = simplejson.dumps(errors)
            return json
        else:
            return 0
    else:
        return 1
