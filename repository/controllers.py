from django.core.exceptions import ObjectDoesNotExist

from models import Project, PanelTemplate, SitePanel, Site, Marker
from collections import Counter


def validate_panel_template_request(data, user):
    """
    Validate the panel:
        - Ensure project and parent_panel (if present) belong to same project
        - Ensure user has privileges to create panel template
        - No duplicate markers in a parameter
        - No fluorochromes in a scatter parameter
        - No markers in a scatter parameter
        - No duplicate fluorochrome + value type combinations
        - No duplicate forward scatter + value type combinations
        - No duplicate side scatter + value type combinations
    """
    errors = {}
    parent_template = None
    staining = None
    can_have_uns = None
    can_have_iso = None

    try:
        project = Project.objects.get(id=data['project'])
    except ObjectDoesNotExist:
        errors['project'] = ["Project does not exist"]
        project = None

    if project:
        # check for project add permission
        if not project.has_add_permission(user):
            errors['project'] = ["Project add permission required"]

    if not 'staining' in data:
        errors['staining'] = ["Staining is required"]
    else:
        staining = data['staining']

    if 'parent_panel' in data:
        if data['parent_panel']:  # may be None
            try:
                parent_template = PanelTemplate.objects.get(id=data['parent_panel'])
            except ObjectDoesNotExist:
                errors['parent_panel'] = ["Parent template does not exist"]

    if len(errors) > 0:
        return errors

    if staining == 'FS' and parent_template:
        errors['staining'] = ["Full stain templates cannot have parents"]
    elif staining == 'FM':
        if not parent_template:
            errors['staining'] = ["FMO templates require full stain parent"]
        elif parent_template.staining != 'FS':
            errors['staining'] = ["FMO templates require full stain parent"]
    elif staining == 'IS':
        if not parent_template:
            errors['staining'] = ["ISO templates require full stain parent"]
        elif parent_template.staining != 'FS':
            errors['staining'] = ["ISO templates require full stain parent"]
    elif staining == 'CB':
        if not parent_template:
            errors['staining'] = [
                "Compensation bead panels require a parent full stain panel"
            ]
        elif parent_template.staining != 'FS':
            errors['staining'] = [
                "Compensation bead panels require a parent full stain panel"
            ]

    # Parameter validation
    if staining == 'FS':
        can_have_uns = False
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
    elif staining == 'CB':
        can_have_uns = False
        can_have_iso = False
    else:
        errors['staining'] = ["Invalid staining type '%s'" % staining]

    # template must have parameters
    if not 'parameters' in data:
        errors['parameters'] = ["Parameters are required"]
    elif not len(data['parameters']) > 0:
        errors['parameters'] = ["Specify at least one parameter"]

    if len(errors) > 0:
        return errors

    param_counter = Counter()
    fmo_count = 0
    iso_count = 0
    param_errors = []
    for param in data['parameters']:
        skip = False  # used for continuing to next loop iteration
        if not 'parameter_type' in param:
            param_errors.append('Function is required')
            skip = True
        if not 'parameter_value_type' in param:
            param_errors.append('Value type is required, use null for None')
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

        # validate param types
        param_type = param['parameter_type']
        if param_type == 'UNS':
            fmo_count += 1
        if param_type == 'ISO':
            iso_count += 1

        if param_type == 'UNS' and not can_have_uns:
            param_errors.append(
                "Only FMO & Unstained panels can include an " +
                "unstained parameter")
        if param_type == 'ISO' and not can_have_iso:
            param_errors.append(
                "Only Isotype control panels can include an " +
                "isotype control parameter")

        # comp bead panels can only have scatter, bead, and time channels
        if staining == 'CB':
            if param_type not in ['FSC', 'SSC', 'BEA', 'TIME']:
                param_errors.append(
                    "Only scatter, bead, and time channels are allowed " +
                    "in bead panels"
                )
            if len(marker_set) > 0:
                param_errors.append(
                    "Markers are not allowed in bead panels"
                )

        # value type is NOT required for panel templates,
        # allows site panel implementations to have different values types
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

        # exclusion must be a fluorescence channel
        if param_type == 'EXC' and not fluorochrome_id:
            param_errors.append(
                "An exclusion channel must include a fluorochrome.")

        if param_type == 'BEA' and not fluorochrome_id:
            param_errors.append(
                "A bead channel must include a fluorochrome.")

        # check for fluoro or markers in scatter channels
        if param_type == 'FSC' or param_type == 'SSC':
            if fluorochrome_id:
                param_errors.append(
                    "A scatter channel cannot have a fluorochrome.")
            if len(marker_set) > 0:
                param_errors.append(
                    "A scatter channel cannot have an marker.")

        # check that fluoro-conj-ab channels specify either a fluoro or a
        # marker. If the fluoro is absent it means the panel template
        # allows flexibility in the site panel implementation.
        if param_type == 'FCM':
            if not fluorochrome_id and len(marker_set) == 0:
                param_errors.append(
                    "A fluorescence conjugated marker channel must " +
                    "specify either a fluorochrome or a marker (or both).")

        # make a list of the combination for use in the Counter
        param_components = [param_type, value_type]
        if fluorochrome_id:
            param_components.append(fluorochrome_id)
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

    # make sure FMO templates have at least one FMO channel &
    # ISO templates have at least one ISO channel
    if staining == 'FM' and fmo_count <= 0:
        param_errors.append("FMO templates require at least 1 FMO channel")
    elif staining == 'IS' and iso_count <= 0:
        param_errors.append("ISO templates require at least 1 ISO channel")

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
        - No fluorochromes in a scatter parameter
        - No markers in a scatter parameter
        - Fluoroscent parameter must specify a fluorochrome
        - No duplicate fluorochrome + value type combinations
        - No duplicate forward scatter + value type combinations
        - No duplicate side scatter + value type combinations

    Bead panels have different validation, but a little simpler:
        - The can only contain FSC, SSC, BEA, and TIM params
        - Markers aren't allowed in any param
        - they must have a parent bead template

    Returns a dictionary of errors, with key as error field and value is a
    list of error messages pertaining to that field.
    An empty dictionary means successful validation
    """
    errors = {}
    panel_template = None
    site = None
    user_sites = None
    can_have_uns = None
    can_have_iso = None

    if 'panel_template' in data:
        try:
            panel_template = PanelTemplate.objects.get(id=data['panel_template'])
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
    if not site in user_sites:
        errors['site'] = [
            "You do not have permission to create panels for this site"]

    # validate panel template and site are in same project
    if site.project_id != panel_template.project_id:
        errors['panel_template'] = ["Panel template is required"]

    if len(errors) > 0:
        return errors

    staining = panel_template.staining
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
    elif staining == 'CB':
        can_have_uns = False
        can_have_iso = False
    else:
        errors['panel_template'] = ["Invalid staining type '%s'" % staining]

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
        if param_type == 'BEA' and len(marker_set) > 0:
            param_errors.append(
                "Bead parameters cannot have markers")

        # value type is required
        value_type = param['parameter_value_type']
        if not value_type:
            param_errors.append("Value type is required")

        fluorochrome_id = param['fluorochrome']

        # exclusion must be a fluorescence channel
        if param_type == 'EXC' and not fluorochrome_id:
            param_errors.append(
                "An exclusion channel must be a fluorescence channel")

        # exclusion must be a fluorescence channel
        if param_type == 'BEA' and not fluorochrome_id:
            param_errors.append(
                "Bead parameters must include a fluorochrome")

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

            if ppp.paneltemplateparameter_set.count() > 0:
                if ppp.paneltemplateparameter_set.count() != len(
                        param_dict[d]['marker_id_set']):
                    # no match
                    continue

                should_continue = False
                for ppp_marker in ppp.paneltemplateparameter_set.all():
                    if str(ppp_marker.marker.id) not in param_dict[d]['marker_id_set']:
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
        if not 'panel_template' in errors:
            errors['panel_template'] = []

        errors['panel_template'].append(
            "Project parameter id %d was not used" % ppp.id)

    if len(param_errors) > 0:
        errors['parameters'] = param_errors
    return errors


def find_matching_site_panel(pnn_list, panel_template, site):
    site_panel_prospects = SitePanel.objects.filter(
        panel_template=panel_template,
        site=site
    )

    for site_panel in site_panel_prospects:
        panel_text_set = set(
            site_panel.sitepanelparameter_set.all().exclude(
                parameter_type__in=['FSC', 'SSC', 'TIM', 'NUL']
            ).values_list('fcs_text', flat=True)
        )
        if len(panel_text_set.symmetric_difference(pnn_list)) == 0:
            return site_panel

    return None
