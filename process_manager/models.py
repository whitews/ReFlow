import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from repository.models import SampleSet


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

    allow_multiple = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        help_text="Whether multiple input values for this input are allowed"
    )

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
    # unique_together doesn't work for forms with any of the
    # unique together fields excluded
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
                "This input name is already used in this process. " +
                "Choose a different name."
            )

    def __unicode__(self):
        return u'%s (Process: %s)' % (
            self.input_name,
            self.get_process_display(),)


class Worker(models.Model):
    """
    The model representation of a client-side worker.
    """
    user = models.OneToOneField(User, null=False, blank=False, editable=False)
    worker_name = models.CharField(
        "Worker Name",
        unique=True,
        null=False,
        blank=False,
        max_length=128)

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


class ProcessRequest(models.Model):
    """
    An formal request for a Process to be executed on a SampleSet
    (collection of Samples).
    """
    process = models.ForeignKey(Process)
    sample_set = models.ForeignKey(
        SampleSet,
        null=False,
        blank=False)
    request_user = models.ForeignKey(
        User, null=False,
        blank=False,
        editable=False)
    request_date = models.DateTimeField(
        editable=False,
        auto_now_add=True)
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        editable=False)
    # optional FK to the worker that is assigned or has completed the request
    worker = models.ForeignKey(
        Worker,
        null=True,
        blank=True)

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

    def save(self, *args, **kwargs):
        if not self.id:
            self.request_date = datetime.datetime.now()
            self.status = 'Pending'
        if self.worker:
            self.status = 'Working'
        super(ProcessRequest, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s (Date: %s)' % (
            self.process.process_name,
            self.request_date,)


class ProcessRequestInputValue(models.Model):
    """
    The actual value to be used for a specific ProcessInput
    for a specific ProcessRequest
    """
    process_request = models.ForeignKey(ProcessRequest)
    process_input = models.ForeignKey(ProcessInput)
    # all values get transmitted in JSON format via REST,
    # so everything is a string
    value = models.CharField(null=False, blank=False, max_length=1024)

    class Meta:
        unique_together = (('process_request', 'process_input'),)

    def __unicode__(self):
        return u'%s (%s): %s' % (
            self.process_request.process.process_name,
            self.process_request_id,
            self.process_input.input_name)