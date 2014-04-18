from django.core.exceptions import ObjectDoesNotExist

from models import ProjectPanel, Site
from collections import Counter


def validate_site_panel_request(data, user):
    """
    Validate a proposed site panel from HTTP request data. Nothing is saved
    here, just validated using the following rules
        - Ensure project panel and site belong to same project
        - Ensure user has proper privileges to create site panel
        - Ensure all project panel parameters are present
        - No duplicate markers in a parameter
        - No fluorochromes in a scatter parameter
        - No markers in a scatter parameter
        - Fluoroscent parameter must specify a fluorochrome
        - No duplicate fluorochrome + value type combinations
        - No duplicate forward scatter + value type combinations
        - No duplicate side scatter + value type combinations

    Returns a dictionary of errors, with key as error field and value is a
    list of error messages pertaining to that field.
    An empty dictionary means successful validation
    """
    errors = {}
    project_panel = None
    site = None
    user_sites = None
    can_have_uns = None
    can_have_iso = None

    if 'project_panel' in data:
        try:
            project_panel = ProjectPanel.objects.get(id=data['project_panel'])
            user_sites = Site.objects.get_sites_user_can_add(
                user, project_panel.project).order_by('site_name')
        except ObjectDoesNotExist:
            errors['project_panel'] = ["Project panel does not exist"]
    else:
        errors['project_panel'] = ["Project panel is required"]

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
    if not site in user_sites:
        errors['site'] = [
            "You do not have permission to create panels for this site"]

    # validate project panel and site are in same project
    if site.project_id != project_panel.project_id:
        errors['project_panel'] = ["Project panel is required"]

    if len(errors) > 0:
        return errors

    staining = project_panel.staining
    if staining == 'FS':
        can_have_uns = True
        can_have_iso = False
    elif staining == 'FM':
        can_have_uns = True
        can_have_iso = False
    elif staining == 'IS':
        can_have_uns = False
        can_have_iso = True
    elif staining == 'US':
        can_have_uns = True
        can_have_iso = False
    else:
        errors['project_panel'] = ["Invalid staining type '%s'" % staining]

    # site panel must have parameters
    if not 'parameters' in data:
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
        if not 'fcs_number' in param:
            param_errors.append('FCS number is required')
            skip = True
        if not 'fcs_text' in param:
            param_errors.append('FCS text is required')
            skip = True
        if not 'fcs_opt_text' in param:
            param_errors.append(
                'FCS optional text is required, use null for None')
            skip = True
        if not 'parameter_type' in param:
            param_errors.append('Function is required')
            skip = True
        if not 'parameter_value_type' in param:
            param_errors.append('Value type is required')
            skip = True
        if not 'markers' in param:
            param_errors.append(
                'Markers is a required field, use an empty array for None')
            skip = True
        if not 'fluorochrome' in param:
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
        if param_type == 'UNS' and not can_have_uns:
            param_errors.append(
                "Only Full Stain, FMO, & Unstained panels can " +
                "include an unstained parameter")
        if param_type == 'ISO' and not can_have_iso:
            param_errors.append(
                "Only Isotype control panels can include an " +
                "isotype control parameter")

        # value type is required
        value_type = param['parameter_value_type']
        if not value_type:
            param_errors.append("Value type is required")

        fluorochrome_id = param['fluorochrome']

        # exclusion must be a fluorescence channel
        if param_type == 'EXC' and not fluorochrome_id:
            param_errors.append(
                "An exclusion channel must be a fluorescence channel")

        # check for fluoro or markers in scatter channels
        if param_type in ['FSC', 'SSC']:
            if fluorochrome_id:
                param_errors.append(
                    "A scatter channel cannot have a fluorochrome")
            if len(marker_set) > 0:
                param_errors.append(
                    "A scatter channel cannot have a marker")

        # check that fluoro conjugated ab channels specify either a
        # fluoro OR marker OR both
        if param_type == 'FCM':
            if not fluorochrome_id or len(marker_set) == 0:
                param_errors.append(
                    "A fluorescence conjugated marker channel must " +
                    "specify a fluorochrome and at least one marker")

        # Unstained channels can't have a fluoro and must have an marker
        if param_type == 'UNS':
            if fluorochrome_id:
                param_errors.append(
                    "Unstained channels CANNOT " +
                    "have a fluorochrome")
            if len(marker_set) == 0:
                param_errors.append(
                    "Unstained channels " +
                    "must specify at least one marker")

        # Iso control & Viability channels must have a fluoro and
        # can't have markers
        if param_type == 'ISO':
            if not fluorochrome_id:
                param_errors.append(
                    "Isotype control channels must " +
                    "have a fluorochrome")
            if len(marker_set) > 0:
                param_errors.append(
                    "Isotype control channels " +
                    "CANNOT have any markers")

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
        # but, unstained params aren't required to be unique
        if param_type not in ['UNS', 'NUL']:
            param_components = [param_type, value_type]
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
    project_panel_parameters = project_panel.projectpanelparameter_set.all()
    matching_ids = []
    print param_dict
    for ppp in project_panel_parameters:
        # first look for parameter type matches
        for d in param_dict:
            if ppp.parameter_type != param_dict[d]['parameter_type']:
                # no match
                print "function mismatch"
                continue

            if ppp.parameter_value_type:
                if ppp.parameter_value_type != param_dict[d]['parameter_value_type']:
                    # no match
                    print "value type mismatch"
                    continue

            if ppp.fluorochrome_id:
                if str(ppp.fluorochrome_id) != param_dict[d]['fluorochrome_id']:
                    # no match
                    print "fluoro mismatch %d" % ppp.fluorochrome_id
                    continue

            if ppp.projectpanelparametermarker_set.count() > 0:
                if ppp.projectpanelparametermarker_set.count() != len(
                        param_dict[d]['marker_id_set']):
                    # no match
                    print "marker length mismatch"
                    continue

                should_continue = False
                for ppp_marker in ppp.projectpanelparametermarker_set.all():
                    if ppp_marker.marker.id not in param_dict[d]['marker_id_set']:
                        # no match
                        print "marker mismatch"
                        should_continue = True
                        break
                if should_continue:
                    continue
            # if we get here where are we?
            matching_ids.append(ppp.id)
            break

    # At the end there should be no project parameters on our list,
    # they all must be implemented by the site panel
    project_panel_parameters = project_panel_parameters.exclude(
        id__in=matching_ids)
    for ppp in project_panel_parameters:
        if not 'project_panel' in errors:
            errors['project_panel'] = []

        errors['project_panel'].append(
            "Project parameter id %d was not used" % ppp.id)

    if len(param_errors) > 0:
        errors['parameters'] = param_errors
    return errors