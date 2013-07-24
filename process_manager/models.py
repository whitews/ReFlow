import datetime
from string import join

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from repository.models import SampleSet
from reflow.settings import MEDIA_ROOT


class Process(models.Model):
    """
    The model representation of a specific workflow.
    """
    process_name = models.CharField(
        "Process Name",
        unique=True,
        null=False,
        blank=False,
        max_length=128,
        help_text="The name of the process (must be unique)")
    process_description = models.TextField(
        "Process Description",
        null=True,
        blank=True,
        help_text="A short description of the process")

    def __unicode__(self):
        return u'%s' % (self.process_name,)


class ProcessInput(models.Model):
    """
    Defines an input parameter for a Process
    """
    process = models.ForeignKey(Process)
    input_name = models.CharField(
        "Input Name",
        unique=False,
        null=False,
        blank=False,
        max_length=128)

    input_description = models.TextField(
        "Process Input Description",
        null=True,
        blank=True,
        help_text="A short description of the input parameter")

    VALUE_TYPE_CHOICES = (
        ('int', 'Integer'),
        ('dec', 'Decimal'),
        ('txt', 'Text String'),
    )

    value_type = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        choices=VALUE_TYPE_CHOICES)

    # Should we add minimum/maximum values???

    default_value = models.CharField(null=True, blank=True, max_length=1024)

    class Meta:
        unique_together = (('process', 'input_name'),)

    # override clean to prevent duplicate input names for a process input...
    # unique_together doesn't work for forms with any of the unique together fields excluded
    def clean(self):
        """
        Verify the process & input_name combination is unique
        """

        qs = ProcessInput.objects.filter(
            process=self.process,
            input_name=self.input_name)\
            .exclude(
                id=self.id)

        if qs.exists():
            raise ValidationError(
                "This input name is already used in this process. Choose a different name."
            )

    def __unicode__(self):
        return u'%s (Process: %s)' % (self.input_name, self.process.process_name,)


class Worker(models.Model):
    """
    The model representation of a client-side worker. A worker should be registered
    as capable of performing a Process via the WorkerProcessMap.
    """
    user = models.OneToOneField(User, null=False, blank=False, editable=False)
    worker_name = models.CharField(
        "Worker Name",
        unique=True,
        null=False,
        blank=False,
        max_length=128)

    worker_version = models.CharField(
        "Worker Version",
        unique=False,
        null=False,
        blank=False,
        max_length=256)

    worker_hostname = models.CharField(
        "Worker Hostname",
        unique=False,
        null=False,
        blank=False,
        max_length=256)

    def save(self, *args, **kwargs):
        if not User.objects.filter(username=self.worker_name).exists():
            # ok to create user, and w/o password since it will not allow login
            user = User.objects.create_user(username=self.worker_name)
            # create auth token for REST API usage
            Token.objects.create(user=user)
            # associate worker to new user
            self.user = user
        super(Worker, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % (self.worker_name,)


class WorkerProcessMap(models.Model):
    """
    Registers a Worker to a Process, enabling a the Worker to take assignment of a
    ProcessRequest.
    """
    worker = models.ForeignKey(Worker)
    process = models.ForeignKey(Process)

    class Meta:
        unique_together = (('worker', 'process'),)

    def __unicode__(self):
        return u'%s-%s' % (self.worker.worker_name, self.process.process_name)


class ProcessRequest(models.Model):
    """
    An formal request for a Process to be executed on a SampleSet (collection of Samples).
    """
    process = models.ForeignKey(Process)
    # optional foreign key to a data set
    sample_set = models.ForeignKey(SampleSet, null=True, blank=True)
    request_user = models.ForeignKey(User, null=False, blank=False, editable=False)
    request_date = models.DateTimeField(editable=False, auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True, editable=False)
    # optional FK to the worker that is assigned or has completed the request
    worker = models.ForeignKey(Worker, null=True, blank=True)

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Working', 'Working'),
        ('Error', 'Error'),
        ('Completed', 'Completed'),
    )

    status = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        choices=STATUS_CHOICES)

    def is_assignable(self):
        """
        Returns True if all input values are given and status is Pending
        """
        if self.status != 'Pending':
            return False

        possible_input_id_list = self.process.processinput_set.all().values_list('id', flat=True).order_by('id')
        actual_input_id_list = self.processrequestinputvalue_set.all().values_list('process_input_id', flat=True).order_by('process_input_id')

        if possible_input_id_list != actual_input_id_list:
            return False

        return True

    def save(self, *args, **kwargs):
        if not self.id:
            self.request_date = datetime.datetime.now()
            self.status = 'Pending'
        super(ProcessRequest, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s (Date: %s)' % (self.process.process_name, self.request_date,)


class ProcessRequestInputValue(models.Model):
    """
    The actual value to be used for a specific ProcessInput for a specific ProcessRequest
    """
    process_request = models.ForeignKey(ProcessRequest)
    process_input = models.ForeignKey(ProcessInput)
    # all values get transmitted in JSON format via REST, so everything is a string
    value = models.CharField(null=False, blank=False, max_length=1024)

    class Meta:
        unique_together = (('process_request', 'process_input'),)

    def __unicode__(self):
        return u'%s (%s): %s' % (
            self.process_request.process.process_name,
            self.process_request_id,
            self.process_input.input_name)


def process_request_output_file_path(instance, filename):
    process_request_id = instance.process_request_id

    upload_dir = join([str(process_request_id), str(filename)], "/")
    upload_dir = join([MEDIA_ROOT, upload_dir], '')

    return upload_dir


class ProcessOutput(models.Model):
    """
    The output data generated by a Worker for a completed ProcessRequest. The
    actual data is stored as a FileField (should be in JSON format)
    """
    process_request = models.ForeignKey(ProcessRequest)
    output_file = models.FileField(
        upload_to=process_request_output_file_path,
        null=False,
        blank=False)

    def __unicode__(self):
        return u'%s (Process: %s)' % (self.process_request_id, self.output_file)