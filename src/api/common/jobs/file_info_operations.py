import logging

from config.celery import CeleryBaseTask
from apps.references.models import Files

class FileInfoWrite(CeleryBaseTask):
    
    def run(self, files, model):
        log = logging.getLogger('FileInfoWrite jobs')
        try:
            files_array = files.get('data', [])
            for file in files_array:
                Files.objects.create(
                    file_id = file.get('id'),
                    name = file.get('name'),
                    real_name = file.get('original_name'),
                    size = file.get('size'),
                    format = file.get('ext'),
                    ext_id = model.get('id'),
                    ext_type = model.get('name'),
                    action_id = 1
                )

        except Exception as e:
            log.error(f"Error FileInfoWrite: {e}")
            raise Exception(e)


class FileInfoDelete(CeleryBaseTask):
    
    def run(self, file_ids):
        log = logging.getLogger('FileInfoDelete jobs')
        try:
            Files.objects.filter(file_id__in=file_ids).delete()

        except Exception as e:
            log.error(f"Error FileInfoDelete: {e}")
            raise Exception(e)