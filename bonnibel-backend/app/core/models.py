import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, DateTime, BigInteger, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# --- Base ---

class Base(DeclarativeBase):
    pass

# --- Enums ---

class ProjectRole(str, enum.Enum):
    OWNER = "OWNER"
    DEVELOPER = "DEVELOPER"
    REVIEWER = "REVIEWER"

class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BANNED = "BANNED"

class IntegrationProvider(str, enum.Enum):
    GITHUB = "GITHUB"
    JIRA = "JIRA"
    CONFLUENCE = "CONFLUENCE"

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"
    CLOSED = "CLOSED"

class PullRequestStatus(str, enum.Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"
    CLOSED = "CLOSED"

class TaskEventType(str, enum.Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    COMMENT_ADDED = "COMMENT_ADDED"

class NotificationType(str, enum.Enum):
    MENTION = "MENTION"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    PR_REVIEW_REQUESTED = "PR_REVIEW_REQUESTED"
    STATUS_CHANGED = "STATUS_CHANGED"
    TASK_UPDATED = "TASK_UPDATED"
    PR_CREATED = "PR_CREATED"
    PR_REVIEWED = "PR_REVIEWED"
    CHAT_MESSAGE = "CHAT_MESSAGE"


# --- Models ---

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = mapped_column(String)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    auth: Mapped["Auth"] = relationship(back_populates="user", uselist=False)
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Auth(Base):
    __tablename__ = "auth"

    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), primary_key=True)
    pass_hash: Mapped[str] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="auth")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.project_id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), primary_key=True)
    role: Mapped[ProjectRole] = mapped_column()


class ProjectIntegration(Base):
    __tablename__ = "project_integrations"

    integration_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.project_id"))
    external_id: Mapped[str] = mapped_column(String)
    provider: Mapped[IntegrationProvider] = mapped_column()
    access_token: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class WebhookSecret(Base):
    __tablename__ = "webhook_secrets"

    webhook_secret_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    integration_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("project_integrations.integration_id"))
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.project_id"))
    provider: Mapped[IntegrationProvider] = mapped_column()
    secret: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.project_id"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO)
    
    assignee_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.user_id"))
    reviewer_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.user_id"))
    
    git_branch_name: Mapped[Optional[str]] = mapped_column(String)
    jira_issue_key: Mapped[Optional[str]] = mapped_column(String)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class TaskSubscription(Base):
    __tablename__ = "task_subscriptions"

    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.task_id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Docs(Base):
    __tablename__ = "docs"

    docs_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.task_id"))
    title: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    external_id: Mapped[Optional[str]] = mapped_column(String)


class PullRequest(Base):
    __tablename__ = "pull_requests"

    pull_request_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.task_id"))
    external_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.user_id"))
    status: Mapped[PullRequestStatus] = mapped_column(default=PullRequestStatus.OPEN)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    merged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.task_id"))
    author_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TaskHistory(Base):
    __tablename__ = "task_history"

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.task_id"))
    type: Mapped[TaskEventType] = mapped_column()
    actor_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String)


class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"))
    type: Mapped[NotificationType] = mapped_column()
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    link_url: Mapped[Optional[str]] = mapped_column(String)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TaskRecipientSnapshot(Base):
    """Minimal task context owned by the notification module to resolve recipients."""

    __tablename__ = "task_recipient_snapshots"

    task_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    owner_id: Mapped[Optional[str]] = mapped_column(String)
    assignee_id: Mapped[Optional[str]] = mapped_column(String)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String)
    title: Mapped[Optional[str]] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
