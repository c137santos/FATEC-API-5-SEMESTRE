# coding: utf-8
import logging

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from django.views.decorators.http import require_http_methods

from ..commons.django_views_utils import ajax_login_required


from .service import cards_svc


logger = logging.getLogger(__name__)



@csrf_exempt
@ajax_login_required
def add_card(request):
    """Adiciona Card"""
    logger.info("API add new card.")
    body = json.loads(request.body)
    description = body.get("description")

    if not description:
        raise ValueError("body.card.description: Field required (missing)")
    if type(description) not in [str]:
        raise ValueError("body.card.description: Input should be a valid string (string_type)")

    description = str(description)
    if len(description) <= 2:
        raise ValueError(
            "body.card.description: Value error, It must be at least 3 characteres long. (value_error)"
        )

    new_card = cards_svc.add_card(description)

    return JsonResponse(new_card, status=201)



@require_http_methods(["GET"])
@ajax_login_required

def list_cards(request):
    """Lista Cards"""
    logger.info("API list cards")
    cards = cards_svc.list_cards()
    return JsonResponse({"cards": cards})
