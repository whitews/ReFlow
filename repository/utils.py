from django.core.exceptions import ValidationError


def apply_panel_to_sample(panel, sample):
    """
    Updates SampleParameterMap instances for provided Sample matching the
    Parameters in the provided SitePanel.
    Note that the panel and sample provided must have the same parent site and
    the sample must have existing SampleParameterMap relations
    (created when Sample was saved).

    Returns 0 status if successful

    sample - The Sample instance for which the SampleParameterMaps will be created
    panel - The SitePanel instance providing the parameters to apply to the sample
    """

    if panel.site != sample.site:
        raise ValidationError("Panel does not belong to the Sample's Site")

    sample_parameters = sample.sampleparametermap_set.all()
    if sample_parameters.count() == 0:
        raise ValidationError("No Sample parameters found")
    panel_parameters = panel.panelparametermap_set.all()

    if sample_parameters.count() != panel_parameters.count():
        raise ValidationError("Sample parameters not equal to Site Panel parameters")

    for sample_param in sample_parameters:
        if sample_param.parameter or sample_param.value_type:
            raise ValidationError("Sample parameter is already specified")

        try:
            # Verify sample parameter text matches a parameter in selected panel
            panel_param = panel_parameters.get(
                fcs_text=sample_param.fcs_text,
                fcs_opt_text=sample_param.fcs_opt_text)
        except:
            raise ValidationError("Site Panel doesn't match Sample parameters")

        # ok, we've got a match, now verify the fcs_opt_text matches
        sample_param.parameter = panel_param.parameter
        sample_param.value_type = panel_param.value_type

    for sample_param in sample_parameters:
        sample_param.save()

    return 0
