"""Testy jednostkowe modułu analytics (AnalyticsService.get_overview)."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.core.models import Project, Task, TaskStatus
from app.modules.analytics.service import AnalyticsService

PROJECT_ID = 1


def _project(db, owner_id: str):
    db.add(Project(project_id=PROJECT_ID, owner_id=owner_id, name="Demo", description=""))
    db.commit()


def _task(db, **kwargs):
    now = datetime.utcnow()
    defaults = dict(
        project_id=PROJECT_ID,
        title="t",
        description="",
        status=TaskStatus.TODO,
        assignee_id=None,
        reviewer_id=None,
        created_at=now,
        updated_at=now,
        closed_at=None,
    )
    defaults.update(kwargs)
    task = Task(**defaults)
    db.add(task)
    db.commit()
    return task


def test_overview_empty_project(db, run, make_user):
    make_user("u1", "u1@a.pl")
    _project(db, "u1")

    out = run(AnalyticsService().get_overview(db, PROJECT_ID))

    assert out.taskCount == 0
    assert out.doneTasks == 0
    assert out.openTasks == 0
    assert out.completionRate == 0.0
    assert out.unassignedTasks == 0
    assert out.staleTasks == 0
    assert out.avgCycleTimeHours is None
    assert out.tasksByStatus == {}
    assert out.tasksByUser == {}
    assert out.tasksByReviewer == {}
    assert out.wipByUser == {}
    assert out.throughputByDay == {}


def test_overview_full_kpis(db, run, make_user):
    make_user("u1", "ala@a.pl")
    make_user("u2", "bob@a.pl")
    _project(db, "u1")

    now = datetime.utcnow()
    # A: ala assignee, bob reviewer, IN_PROGRESS (świeże)
    _task(db, assignee_id="u1", reviewer_id="u2", status=TaskStatus.IN_PROGRESS, updated_at=now)
    # B: bob assignee, ala reviewer, DONE, cykl 48h
    _task(db, assignee_id="u2", reviewer_id="u1", status=TaskStatus.DONE,
          created_at=now - timedelta(days=3), closed_at=now - timedelta(days=1),
          updated_at=now - timedelta(days=1))
    # C: nieprzypisane, TODO, stale (10 dni)
    _task(db, status=TaskStatus.TODO, created_at=now - timedelta(days=10),
          updated_at=now - timedelta(days=10))
    # D: ala assignee, IN_REVIEW (drugi WIP dla ali)
    _task(db, assignee_id="u1", reviewer_id="u2", status=TaskStatus.IN_REVIEW, updated_at=now)
    # E: bob assignee, DONE, cykl 24h (inny dzień zamknięcia)
    _task(db, assignee_id="u2", status=TaskStatus.DONE,
          created_at=now - timedelta(days=5), closed_at=now - timedelta(days=4),
          updated_at=now - timedelta(days=4))

    out = run(AnalyticsService().get_overview(db, PROJECT_ID))

    assert out.taskCount == 5
    assert out.doneTasks == 2
    assert out.openTasks == 3
    assert out.completionRate == 40.0
    assert out.unassignedTasks == 1
    assert out.staleTasks == 1
    assert out.avgCycleTimeHours == 36.0  # (48 + 24) / 2

    assert out.tasksByStatus == {"TODO": 1, "IN_PROGRESS": 1, "IN_REVIEW": 1, "DONE": 2}
    # mapowane po mailu, nieprzypisane jako "(brak)"
    assert out.tasksByUser == {"ala@a.pl": 2, "bob@a.pl": 2, "(brak)": 1}
    assert out.tasksByReviewer == {"bob@a.pl": 2, "ala@a.pl": 1, "(brak)": 2}
    assert out.wipByUser == {"ala@a.pl": 2}
    # dwa różne dni zamknięcia, po jednym zadaniu
    assert sum(out.throughputByDay.values()) == 2
    assert len(out.throughputByDay) == 2


def test_completion_rate_all_done(db, run, make_user):
    make_user("u1", "u1@a.pl")
    _project(db, "u1")
    _task(db, status=TaskStatus.DONE, closed_at=datetime.utcnow())
    _task(db, status=TaskStatus.DONE, closed_at=datetime.utcnow())

    out = run(AnalyticsService().get_overview(db, PROJECT_ID))

    assert out.completionRate == 100.0
    assert out.openTasks == 0
