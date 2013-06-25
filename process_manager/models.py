from django.db import models
from django.contrib.auth.models import User
import datetime


class Process(models.Model):
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
    process = models.ForeignKey(Process)
    input_name = models.CharField(
        "Input Name",
        unique=False,
        null=False,
        blank=False,
        max_length=128)

    VALUE_TYPE_CHOICES = (
        ('int', 'Integer'),
        ('float', 'Float'),
        ('str', 'Text String'),
    )

    value_type = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        choices=VALUE_TYPE_CHOICES)

    def __unicode__(self):
        return u'%s (Process: %s)' % (self.input_name, self.process.process_name,)


class ProcessOutput(models.Model):
    process = models.ForeignKey(Process)
    output_name = models.CharField(
        "Output Name",
        unique=False,
        null=False,
        blank=False,
        max_length=128)

    VALUE_TYPE_CHOICES = (
        ('int', 'Integer'),
        ('dec', 'Decimal'),
        ('str', 'Text String'),
    )

    value_type = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        choices=VALUE_TYPE_CHOICES)

    def __unicode__(self):
        return u'%s (Process: %s)' % (self.output_name, self.process.process_name,)


class Worker(models.Model):
    worker_name = models.CharField(
        "Worker Name",
        unique=True,
        null=False,
        blank=False,
        max_length=128)

    def __unicode__(self):
        return u'%s' % (self.worker_name,)


class WorkerProcessMap(models.Model):
    worker = models.ForeignKey(Worker)
    process = models.ForeignKey(Process)


class ProcessRequest(models.Model):
    process = models.ForeignKey(Process)
    request_user = models.ForeignKey(User, null=False, blank=False)
    request_date = models.DateTimeField(editable=False)
    completion_date = models.DateTimeField()

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
        super(ProcessRequest, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s (Date: %s)' % (self.process.process_name, self.request_date,)


class ProcessRequestInputValue(models.Model):
    process_request = models.ForeignKey(ProcessRequest)
    process_input = models.ForeignKey(ProcessInput)
    # all values get transmitted in JSON format via REST, so everything is a string
    value = models.CharField(null=False, blank=False, max_length=1024)
