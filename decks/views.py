from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Deck, DeckCard
from cards.models import Card
from api.permissions import IsStaffUser


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStaffUser])
def create_deck(request):
    if request.method == "GET":
        decks = Deck.objects.all().order_by("-is_default", "name", "id")

        # contamos cartas por mazo (eficiente)
        result = []
        for d in decks:
            cards_count = DeckCard.objects.filter(deck=d).count()
            result.append(
                {
                    "id": d.id,
                    "name": d.name,
                    "description": d.description,
                    "is_default": d.is_default,
                    "cards_count": cards_count,
                }
            )

        return Response({"decks": result}, status=status.HTTP_200_OK)

    # POST (igual que tenías)
    deck = Deck.objects.create(
        created_by=request.user,
        name=request.data.get("name", "Deck"),
        description=request.data.get("description", ""),
        is_default=bool(request.data.get("is_default", False)),
    )
    return Response({"id": deck.id, "name": deck.name}, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStaffUser])
def deck_cards(request, deck_id: int):
    # valida que existe el deck
    deck = get_object_or_404(Deck, pk=deck_id)

    if request.method == "GET":
        items = DeckCard.objects.filter(deck_id=deck_id).order_by("order", "id")
        return Response(
            [{"card": dc.card_id, "order": dc.order} for dc in items],
            status=status.HTTP_200_OK,
        )

    # POST: { "cards": [1,2,3] }
    card_ids = request.data.get("cards", [])
    if not isinstance(card_ids, list) or not card_ids:
        return Response(
            {"detail": "cards must be a non-empty list"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    created = 0
    for idx, cid in enumerate(card_ids, start=1):
        # valida card
        get_object_or_404(Card, pk=cid)

        DeckCard.objects.get_or_create(
            deck_id=deck_id,
            card_id=cid,
            defaults={"order": idx},
        )
        created += 1

    return Response({"added": created}, status=status.HTTP_201_CREATED)
