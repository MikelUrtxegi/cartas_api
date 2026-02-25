from django.shortcuts import render
from django.db.models import Count, Sum


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from company_session.models import Session, Group, Vote


def _is_admin_user(user) -> bool:
    return bool(user and user.is_authenticated and user.is_staff)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    if not _is_admin_user(request.user):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    qs = Session.objects.all().order_by("-id")[:50]
    data = [
        {
            "id": s.id,
            "company": s.company_id,
            "language": s.language,
            "status": getattr(s, "status", None),
            "created_at": getattr(s, "created", None),
            "updated_at": getattr(s, "modified", None),
        }
        for s in qs
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_detail(request, session_id: int):
    if not _is_admin_user(request.user):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    try:
        s = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response(
        {
            "id": s.id,
            "company": s.company_id,
            "language": s.language,
            "status": getattr(s, "status", None),
            "created_at": getattr(s, "created", None),
            "updated_at": getattr(s, "modified", None),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_groups(request, session_id: int):
    if not _is_admin_user(request.user):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    groups = Group.objects.filter(session_id=session_id).order_by("id")
    data = [
        {
            "id": g.id,
            "session": g.session_id,
            "name": g.name,
            "join_code": g.join_code,
            "created_at": getattr(g, "created", None),
            "updated_at": getattr(g, "modified", None),
        }
        for g in groups
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_votes(request, session_id: int):
    if not _is_admin_user(request.user):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    votes = (
        Vote.objects.filter(session_id=session_id)
        .select_related("group", "card")
        .order_by("id")
    )
    data = [
        {
            "id": v.id,
            "session": v.session_id,
            "group": v.group_id,
            "card": v.card_id,
            "value": v.value,
            "comment": v.comment,
            "created_at": getattr(v, "created", None),
            "updated_at": getattr(v, "modified", None),
        }
        for v in votes
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    if not _is_admin_user(request.user):
        return Response({"detail": "Forbidden"}, status=403)

    sessions = (
        Session.objects.select_related("company")
        .annotate(
            groups_count=Count("groups"),
            votes_count=Count("votes"),
        )
        .order_by("-id")
    )

    active_sessions = sessions.filter(status="active").count()

    totals = sessions.aggregate(
        total_groups=Sum("groups_count"),
        total_votes=Sum("votes_count"),
    )

    total_groups = totals["total_groups"] or 0
    total_votes = totals["total_votes"] or 0

    sessions_data = []

    for s in sessions[:50]:
        sessions_data.append(
            {
                "id": s.id,
                "company": {
                    "id": s.company.id,
                    "sector": getattr(s.company, "sector", None),
                    "created_at": getattr(s.company, "created", None),
                },
                "status": s.status,
                "groups": s.groups_count,
                "votes": s.votes_count,
            }
        )

    return Response(
        {
            "stats": {
                "activeSessions": active_sessions,
                "totalGroups": total_groups,
                "ratedCards": total_votes,
            },
            "sessions": sessions_data,
        }
    )
