"""Testy jednostkowe modułu chat (ChatService)."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core.models import ChatMessage
from app.modules.chat.service import ChatService

TASK_ID = 1


def test_send_message_returns_author_email(db, run, make_user):
    make_user("u1", "ala@a.pl")
    svc = ChatService()

    payload = run(svc.send_message(db, task_id=TASK_ID, author_id="u1", text="Cześć"))

    assert payload["authorId"] == "u1"
    assert payload["authorEmail"] == "ala@a.pl"
    assert payload["text"] == "Cześć"
    assert payload["taskId"] == TASK_ID
    assert isinstance(payload["messageId"], int)


def test_get_messages_lists_with_email_in_order(db, run, make_user):
    make_user("u1", "ala@a.pl")
    make_user("u2", "bob@a.pl")
    svc = ChatService()

    run(svc.send_message(db, task_id=TASK_ID, author_id="u1", text="pierwsza"))
    run(svc.send_message(db, task_id=TASK_ID, author_id="u2", text="druga"))

    messages = run(svc.get_messages(db, TASK_ID))

    assert [m["text"] for m in messages] == ["pierwsza", "druga"]
    assert messages[0]["authorEmail"] == "ala@a.pl"
    assert messages[1]["authorEmail"] == "bob@a.pl"


def test_get_messages_only_for_task(db, run, make_user):
    make_user("u1", "ala@a.pl")
    svc = ChatService()
    run(svc.send_message(db, task_id=TASK_ID, author_id="u1", text="dla 1"))
    run(svc.send_message(db, task_id=999, author_id="u1", text="dla 999"))

    messages = run(svc.get_messages(db, TASK_ID))

    assert [m["text"] for m in messages] == ["dla 1"]


def test_update_message_by_author(db, run, make_user):
    make_user("u1", "ala@a.pl")
    svc = ChatService()
    sent = run(svc.send_message(db, task_id=TASK_ID, author_id="u1", text="stara"))

    updated = run(svc.update_message(db, message_id=sent["messageId"],
                                     current_user_id="u1", text="nowa"))

    assert updated["text"] == "nowa"
    assert updated["authorEmail"] == "ala@a.pl"


def test_update_message_by_other_forbidden(db, run, make_user):
    make_user("u1", "ala@a.pl")
    make_user("u2", "bob@a.pl")
    svc = ChatService()
    sent = run(svc.send_message(db, task_id=TASK_ID, author_id="u1", text="stara"))

    with pytest.raises(HTTPException) as exc:
        run(svc.update_message(db, message_id=sent["messageId"],
                               current_user_id="u2", text="hack"))
    assert exc.value.status_code == 403


def test_update_missing_message_404(db, run, make_user):
    make_user("u1", "ala@a.pl")
    svc = ChatService()

    with pytest.raises(HTTPException) as exc:
        run(svc.update_message(db, message_id=12345, current_user_id="u1", text="x"))
    assert exc.value.status_code == 404


def test_delete_message_by_author(db, run, make_user):
    make_user("u1", "ala@a.pl")
    svc = ChatService()
    sent = run(svc.send_message(db, task_id=TASK_ID, author_id="u1", text="do usunięcia"))

    run(svc.delete_message(db, message_id=sent["messageId"], current_user_id="u1"))

    assert db.get(ChatMessage, sent["messageId"]) is None


def test_delete_message_by_other_forbidden(db, run, make_user):
    make_user("u1", "ala@a.pl")
    make_user("u2", "bob@a.pl")
    svc = ChatService()
    sent = run(svc.send_message(db, task_id=TASK_ID, author_id="u1", text="moje"))

    with pytest.raises(HTTPException) as exc:
        run(svc.delete_message(db, message_id=sent["messageId"], current_user_id="u2"))
    assert exc.value.status_code == 403
    # wiadomość nadal istnieje
    assert db.get(ChatMessage, sent["messageId"]) is not None
