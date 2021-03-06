from django.core.exceptions import ObjectDoesNotExist

from models import Project, PanelTemplate, Site, Marker, Fluorochrome
from collections import Counter


def validate_panel_template_request(data, user):
    """
    Validate the panel:
        - Ensure user has privileges to create panel template
        - No duplicate markers in a parameter
        - No fluorochrome in a scatter parameter
        - No markers in a scatter parameter
        - No duplicate fluorochrome combinations
        - No duplicate forward scatter + value type combinations
        - No duplicate side scatter + value type combinations
    """
    errors = {}

    try:
        project = Project.objects.get(id=data['project'])
    except ObjectDoesNotExist:
        errors['project'] = ["Project does not exist"]
        project = None

    if project:
        # check for project add permission
        if not project.has_add_permission(user):
            errors['project'] = ["Project add permission required"]

    if len(errors) > 0:
        return errors

    # template must have parameters
    if 'parameters' not in data:
        errors['parameters'] = ["Parameters are required"]
    elif len(data['parameters']) <= 0:
        errors['parameters'] = ["Specify at least one parameter"]

    if len(errors) > 0:
        return errors

    param_counter = Counter()
    param_errors = []
    fluoro_set = set()  # don't allow duplicate fluoro in panel
    for param in data['parameters']:
        skip = False  # used for continuing to next loop iteration
        if 'parameter_type' not in param:
            param_errors.append('Function is required')
            skip = True
        if 'parameter_value_type' not in param:
            param_errors.append('Value type is required')
            skip = True
        if 'markers' not in param:
            param_errors.append(
                'Markers is a required field, use an empty array for None')
            skip = True
        if 'fluorochrome' not in param:
            param_errors.append(
                'Fluorochrome is a required field, use null for None')
            skip = True

        if skip:
            continue

        # check for duplicate markers in a parameter
        marker_set = set()
        for marker in param['markers']:
            if marker in marker_set:
                param_errors.append("A parameter cannot have duplicate markers")
            else:
                marker_set.add(marker)

        # validate param types
        param_type = param['parameter_type']

        # value type is required for panel templates,
        value_type = param['parameter_value_type']

        # validate time channel, must have value type 'T', others cannot have
        # value type 'T'
        if param_type != 'TIM' and value_type == 'T':
            param_errors.append(
                "Only Time channels can have value type 'T'")
        elif param_type == 'TIM' and value_type != 'T':
            param_errors.append(
                "Time channels must have value type 'T'")

        fluorochrome_id = param['fluorochrome']
        if fluorochrome_id:
            if fluorochrome_id in fluoro_set:
                param_errors.append(
                    "Panels cannot have duplicate fluorochromes"
                )
            fluoro_set.add(fluorochrome_id)

        # fluorescence parameters must include a fluorochrome
        if param_type == 'FLR':
            if not fluorochrome_id and len(marker_set) <= 0:
                param_errors.append(
                    "Fluorescence parameters must specify either a marker or " +
                    "a fluorochrome (or both)"
                )

        # check for fluoro or markers in scatter channels
        if param_type == 'FSC' or param_type == 'SSC':
            if fluorochrome_id:
                param_errors.append(
                    "A scatter channel cannot have a fluorochrome.")
            if len(marker_set) > 0:
                param_errors.append(
                    "A scatter channel cannot have an marker.")

        # make a list of the combination for use in the Counter, except that
        # fluoro channels won't use value_type for duplicate check, so we
        # use a dummy value ''
        if param_type == 'FLR':
            param_components = [param_type]
        else:
            param_components = [param_type, value_type]

        if fluorochrome_id:
            try:
                fluoro = Fluorochrome.objects.get(id=fluorochrome_id)
                param_components.append(fluoro.fluorochrome_abbreviation)
            except ObjectDoesNotExist:
                param_errors.append("Chosen fluorochrome doesn't exist")
        for marker_id in sorted(marker_set):
            try:
                marker = Marker.objects.get(id=marker_id)
                param_components.append(marker.marker_abbreviation)
            except ObjectDoesNotExist:
                param_errors.append("Chosen marker doesn't exist")

        param_counter.update([tuple(sorted(param_components))])

    # check for duplicate parameters
    if max(param_counter.values()) > 1:
        error_string = "Duplicate parameters found: "
        for p in param_counter:
            if param_counter[p] > 1:
                error_string += "(" + ", ".join(p) + ")"
        param_errors.append(error_string)

    if len(param_errors) > 0:
        errors['parameters'] = param_errors
    return errors


def validate_site_panel_request(data, user):
    """
    Validate a proposed site panel from HTTP request data. Nothing is saved
    here, just validated using the following rules
        - Ensure panel template and site belong to same project
        - Ensure user has proper privileges to create site panel
        - Ensure all panel template parameters are present
        - No duplicate markers in a parameter
        - No fluorochrome in a scatter parameter
        - No markers in a scatter parameter
        - Fluorescent parameter must specify a fluorochrome
        - The same fluorochrome cannot be present in more than one parameter
        - No duplicate forward scatter + value type combinations
        - No duplicate side scatter + value type combinations

    Returns a dictionary of errors, with key as error field and value is a
    list of error messages pertaining to that field.
    An empty dictionary means successful validation
    """
    errors = {}
    panel_template = None
    site = None
    user_sites = None

    if 'panel_template' in data:
        try:
            panel_template = PanelTemplate.objects.get(
                id=data['panel_template']
            )
            user_sites = Site.objects.get_sites_user_can_add(
                user, panel_template.project).order_by('site_name')
        except ObjectDoesNotExist:
            errors['panel_template'] = ["Panel template does not exist"]
    else:
        errors['panel_template'] = ["Panel template is required"]

    if 'site' in data:
        try:
            site = Site.objects.get(id=data['site'])
        except ObjectDoesNotExist:
            errors['site'] = ["Site does not exist"]
    else:
        errors['site'] = ["Site is required"]

    if len(errors) > 0:
        return errors

    # validate site is in user sites
    if site not in user_sites:
        errors['site'] = [
            "You do not have permission to create panels for this site"]

    # validate panel template and site are in same project
    if site.project_id != panel_template.project_id:
        errors['panel_template'] = [
            "Panel template & site belong to different projects"
        ]

    if len(errors) > 0:
        return errors

    # site panel must have parameters
    if 'parameters' not in data:
        errors['parameters'] = ["Parameters are required"]
    elif not len(data['parameters']) > 0:
        errors['parameters'] = ["Specify at least one parameter"]

    if len(errors) > 0:
        return errors

    param_counter = Counter()
    param_dict = {}
    param_errors = []
    for param in data['parameters']:
        # validate required param fields:
        #     - fcs_number
        #     - fcs_text
        #     - fcs_opt_text
        #     - parameter_type
        #     - parameter_value_type
        #     - markers  ???
        #     - fluorochrome ???
        skip = False  # used for continuing to next loop iteration
        if 'fcs_number' not in param:
            param_errors.append('FCS number is required')
            skip = True
        if 'fcs_text' not in param:
            param_errors.append('FCS text is required')
            skip = True
        if 'fcs_opt_text' not in param:
            param_errors.append(
                'FCS optional text is required, use null for None')
            skip = True
        if 'parameter_type' not in param:
            param_errors.append('Function is required')
            skip = True
        if 'parameter_value_type' not in param:
            param_errors.append('Value type is required')
            skip = True
        if 'markers' not in param:
            param_errors.append(
                'Markers is a required field, use an empty array for None')
            skip = True
        if 'fluorochrome' not in param:
            param_errors.append(
                'Fluorochrome is a required field, use null for None')
            skip = True

        if skip:
            continue

        # check for duplicate markers in a parameter
        marker_set = set()
        for marker in param['markers']:
            if marker in marker_set:
                param_errors.append("A parameter cannot have duplicate markers")
            else:
                marker_set.add(marker)

        # parameter type is required
        param_type = param['parameter_type']
        if not param_type:
            param_errors.append("Function is required for all parameters")

        # value type is required
        value_type = param['parameter_value_type']
        if not value_type:
            param_errors.append("Value type is required")

        fluorochrome_id = param['fluorochrome']

        # fluorescence param must include a fluorochrome
        if param_type == 'FLR' and not fluorochrome_id:
            param_errors.append(
                "An fluorescence channel must include a fluorochrome")

        # check for fluoro or markers in scatter channels
        if param_type in ['FSC', 'SSC']:
            if fluorochrome_id:
                param_errors.append(
                    "A scatter channel cannot have a fluorochrome")
            if len(marker_set) > 0:
                param_errors.append(
                    "A scatter channel cannot have a marker")

        # Time channels cannot have fluoros or markers, must have T value
        if param_type == 'TIM':
            if fluorochrome_id:
                param_errors.append(
                    "Time channels " +
                    "CANNOT have a fluorochrome")
            if len(marker_set) > 0:
                param_errors.append(
                    "Time channels " +
                    "CANNOT have any markers")
            if value_type != 'T':
                param_errors.append(
                    "Time channels " +
                    "must have a T value type")

        # make a list of the combination for use in the Counter
        # ignoring null parameters
        if param_type not in ['NUL']:
            param_components = [param_type]

            # Only consider value_type for scatter & time channels.
            # We don't allow the same fluorochrome in multiple channels
            # regardless of the value type b/c of the difficulties with
            # handling compensation matrices
            if param_type in ['FSC', 'SSC', 'TIM']:
                param_components.append(value_type)
            if fluorochrome_id:
                param_components.append(fluorochrome_id)

            param_counter.update([tuple(sorted(param_components))])

        fcs_number = param['fcs_number']
        param_dict[fcs_number] = {
            'parameter_type': param_type,
            'parameter_value_type': value_type,
            'fluorochrome_id': fluorochrome_id,
            'marker_id_set': marker_set
        }

    # first, check if any params made it through the above for loop
    if len(param_counter.values()) == 0:
        param_errors.append("No valid parameters were specified")

    # check for duplicate parameters
    elif max(param_counter.values()) > 1:
        param_errors.append("Cannot have duplicate parameters")

    # Finally, check that all the project parameters are accounted for
    panel_template_parameters = panel_template.paneltemplateparameter_set.all()
    matching_ids = []
    for ppp in panel_template_parameters:
        # first look for parameter type matches
        for d in param_dict:
            if ppp.parameter_type != param_dict[d]['parameter_type']:
                # no match
                continue

            if ppp.parameter_value_type:
                if ppp.parameter_value_type != param_dict[d]['parameter_value_type']:
                    # no match
                    continue

            if ppp.fluorochrome_id:
                if str(ppp.fluorochrome_id) != str(param_dict[d]['fluorochrome_id']):
                    # no match
                    continue

            if ppp.paneltemplateparametermarker_set.count() > 0:
                if ppp.paneltemplateparametermarker_set.count() != len(
                        param_dict[d]['marker_id_set']):
                    # no match
                    continue

                should_continue = False
                for ppp_marker in ppp.paneltemplateparametermarker_set.all():
                    if ppp_marker.marker.id not in param_dict[d]['marker_id_set']:
                        # no match
                        should_continue = True
                        break
                if should_continue:
                    continue
            # if we get here where are we?
            matching_ids.append(ppp.id)
            break

    # At the end there should be no project parameters on our list,
    # they all must be implemented by the site panel
    panel_template_parameters = panel_template_parameters.exclude(
        id__in=matching_ids)
    for ppp in panel_template_parameters:
        if 'panel_template' not in errors:
            errors['panel_template'] = []

        errors['panel_template'].append(
            "Project parameter id %d was not used" % ppp.id)

    if len(param_errors) > 0:
        errors['parameters'] = param_errors
    return errors


def matches_site_panel_colors(pnn_list, site_panel):
    """
    Returns true or false depending on whether the given pnn_list matches
    the fluorescent parameters of the given site_panel

    :param pnn_list:
    :param site_panel:
    :return: boolean
    """
    panel_text_set = set(
        site_panel.sitepanelparameter_set.all().exclude(
            parameter_type__in=['FSC', 'SSC', 'TIM', 'NUL']
        ).values_list('fcs_text', flat=True)
    )
    if len(panel_text_set.symmetric_difference(pnn_list)) == 0:
        return True

    return False
