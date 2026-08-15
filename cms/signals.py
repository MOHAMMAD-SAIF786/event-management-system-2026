import logging
from django.db.models.signals import pre_save, post_delete

from cms.storage_cleanup import (
    handle_pre_save_image_replacement,
    handle_post_delete_image_cleanup,
)

logger = logging.getLogger("ems.storage_saver")


def register_storage_cleanup_signals():
    """
    Registers pre_save and post_delete signal handlers on all models
    containing FileField or ImageField across the EMS applications.
    """
    try:
        from rooms.models import Room, RoomPage
        from halls.models import Hall, HallGallery, StageDesign, HallPage
        from catering.models import CateringPackage, CateringPage
        from home.models import HomePage
        from cms.models import GalleryItem

        cleanup_models = [
            Room,
            RoomPage,
            Hall,
            HallGallery,
            StageDesign,
            HallPage,
            CateringPackage,
            CateringPage,
            HomePage,
            GalleryItem,
        ]

        for model_cls in cleanup_models:
            pre_save.connect(
                handle_pre_save_image_replacement,
                sender=model_cls,
                dispatch_uid=f"storage_saver_pre_save_{model_cls.__name__}",
            )
            post_delete.connect(
                handle_post_delete_image_cleanup,
                sender=model_cls,
                dispatch_uid=f"storage_saver_post_delete_{model_cls.__name__}",
            )

        logger.info(f"[Storage Saver] Successfully registered 10s delayed image cleanup on {len(cleanup_models)} models.")
    except Exception as e:
        logger.error(f"[Storage Saver] Failed to register cleanup signals: {e}")
