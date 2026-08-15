import os
import threading
import logging
from django.conf import settings
from django.db import models
from django.db.models.fields.files import FieldFile

logger = logging.getLogger("ems.storage_saver")


def delayed_delete_file(file_path, delay_seconds=10):
    """
    Schedules an old/replaced image file on disk for deletion after `delay_seconds` (default 10s).
    Runs asynchronously in a background daemon thread.
    """
    if not file_path or not os.path.exists(file_path):
        return

    # Security check: only delete files residing inside MEDIA_ROOT
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    abs_path = os.path.abspath(file_path)
    if not abs_path.startswith(media_root):
        logger.warning(f"[Storage Saver] Skipped non-media path: {file_path}")
        return

    def _execute_deletion():
        try:
            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                os.remove(abs_path)
                logger.info(f"[Storage Saver] Successfully deleted replaced image after {delay_seconds}s: {abs_path}")
            else:
                logger.debug(f"[Storage Saver] File already removed or missing: {abs_path}")
        except Exception as e:
            logger.error(f"[Storage Saver] Error deleting replaced file {abs_path}: {e}")

    timer = threading.Timer(delay_seconds, _execute_deletion)
    timer.daemon = True
    timer.name = f"StorageSaver-Delete-{os.path.basename(abs_path)}"
    timer.start()
    logger.info(f"[Storage Saver] Queued file deletion in {delay_seconds}s: {abs_path}")


def handle_pre_save_image_replacement(sender, instance, **kwargs):
    """
    Detects if any FileField/ImageField is replaced with a new file.
    Queues the previous file for deletion in 10 seconds.
    """
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.filter(pk=instance.pk).first()
        if not old_instance:
            return

        for field in instance._meta.fields:
            if isinstance(field, (models.ImageField, models.FileField)):
                old_file = getattr(old_instance, field.name, None)
                new_file = getattr(instance, field.name, None)

                # Check if old file existed and differs from new file
                if old_file and old_file.name and (not new_file or old_file.name != getattr(new_file, 'name', str(new_file))):
                    try:
                        old_path = old_file.path
                        # Verify no other row in this table is using the same file
                        is_shared = sender.objects.filter(**{field.name: old_file.name}).exclude(pk=instance.pk).exists()
                        if not is_shared and os.path.exists(old_path):
                            delayed_delete_file(old_path, delay_seconds=10)
                    except (ValueError, AttributeError, NotImplementedError) as err:
                        logger.debug(f"[Storage Saver] Could not resolve old file path: {err}")
    except Exception as e:
        logger.error(f"[Storage Saver] Error in handle_pre_save_image_replacement for {sender.__name__}: {e}")


def handle_post_delete_image_cleanup(sender, instance, **kwargs):
    """
    Detects if an instance with FileField/ImageField is deleted.
    Queues its media files for deletion in 10 seconds.
    """
    try:
        for field in instance._meta.fields:
            if isinstance(field, (models.ImageField, models.FileField)):
                file_obj = getattr(instance, field.name, None)
                if file_obj and file_obj.name:
                    try:
                        file_path = file_obj.path
                        # Verify no other row uses this file
                        is_shared = sender.objects.filter(**{field.name: file_obj.name}).exists()
                        if not is_shared and os.path.exists(file_path):
                            delayed_delete_file(file_path, delay_seconds=10)
                    except (ValueError, AttributeError, NotImplementedError):
                        pass
    except Exception as e:
        logger.error(f"[Storage Saver] Error in handle_post_delete_image_cleanup for {sender.__name__}: {e}")
