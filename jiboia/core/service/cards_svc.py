import logging

from ..models import Card
from jiboia.base.exceptions import BusinessError

logger = logging.getLogger(__name__)


def add_card(new_card: str) -> dict:
    logger.info("SERVICE add new card")
    if not isinstance(new_card, str):
        raise BusinessError("Invalid description")

    if not new_card or not new_card.strip():
        raise BusinessError("Invalid description")

    card = Card(description=new_card)
    card.save()
    logger.info("SERVICE card created.")
    return card.to_dict_json()


def list_cards():
    logger.info("SERVICE list cards")
    cards_list = Card.objects.all()
    return [item.to_dict_json() for item in cards_list]
