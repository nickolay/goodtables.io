from celery import signals

from goodtablesio import models
from goodtablesio.tasks import validate
from goodtablesio.plugins.github.utils import set_commit_status


# Module API

@signals.task_postrun.connect(sender=validate)
def post_task_handler(**kwargs):

    job = kwargs['retval']
    if isinstance(kwargs['retval'], Exception):
        job_id = kwargs['kwargs']['job_id']
        job = models.job.get(job_id)

    if job.get('plugin_name') != 'github':
        return

    task_state = kwargs['state']

    status = job['status']
    plugin_conf = job['plugin_conf']

    if plugin_conf:

        if task_state == 'SUCCESS' and status != 'running':
            github_status = status
        else:
            github_status = 'error'

        set_commit_status(
           github_status,
           owner=plugin_conf['repository']['owner'],
           repo=plugin_conf['repository']['name'],
           sha=plugin_conf['sha'],
           job_id=job['id'])
