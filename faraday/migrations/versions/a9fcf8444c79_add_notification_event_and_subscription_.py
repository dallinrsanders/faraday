"""add_notification_event_and_subscription_model

Revision ID: a9fcf8444c79
Revises: a4def820a5bb
Create Date: 2021-05-28 15:47:13.781453+00:00

"""
from alembic import op
import sqlalchemy as sa
from faraday.server.fields import JSONType

# Added manually for inserts
from sqlalchemy import orm

# revision identifiers, used by Alembic.
revision = 'a9fcf8444c79'
down_revision = '18891ca61db6'
branch_labels = None
depends_on = None


def upgrade():

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('notification_event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event', sa.Enum('new_workspace', 'new_agent', 'new_user', 'new_agentexecution', 'new_executivereport', 'new_vulnerability', 'new_command', 'new_comment', 'update_workspace', 'update_agent', 'update_user', 'update_agent_scan', 'update_executivereport', 'update_vulnerability', 'update_comment', 'delete_workspace', 'delete_agent', 'delete_user', 'delete_executivereport', 'delete_vulnerability', 'delete_comment', name='notification_events'), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=False),
    sa.Column('notification_data', JSONType(), nullable=False),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('workspace_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], )
    )

    # Added manually
    op.add_column('notification_event',
                  sa.Column(
                      'object_type',
                      sa.Enum('vulnerability',
                              'host',
                              'credential',
                              'service',
                              'source_code',
                              'comment',
                              'executive_report',
                              'workspace',
                              'task'
                              'executivereport'
                              'agent',
                              'agentexecution',
                              name='object_types'),
                      nullable=False
                  )
                  )
    ##

    op.create_table('notification_subscription',
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('update_user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['faraday_user.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['update_user_id'], ['faraday_user.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # Added manually
    op.add_column('notification_subscription',
                  sa.Column(
                      'event',
                      sa.Enum('new_workspace',
                              'new_agent',
                              'new_user',
                              'new_agentexecution',
                              'new_executivereport',
                              'new_vulnerability',
                              'new_command',
                              'new_comment',
                              'update_workspace',
                              'update_agent',
                              'update_user',
                              'update_agent_scan',
                              'update_executivereport',
                              'update_vulnerability',
                              'update_comment',
                              'delete_workspace',
                              'delete_agent',
                              'delete_user',
                              'delete_executivereport',
                              'delete_vulnerability',
                              'delete_comment',
                              name='notification_events'),
                      nullable=False)
                  )

    ##

    op.create_table('notification_allowed_roles',
    sa.Column('notification_subscription_id', sa.Integer(), nullable=False),
    sa.Column('allowed_role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['allowed_role_id'], ['notification_roles.id'], ),
    sa.ForeignKeyConstraint(['notification_subscription_id'], ['notification_subscription.id'], )
    )

    op.create_table('notification_subscription_config_base',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subscription_id', sa.Integer(), nullable=False),
    sa.Column('role_level', sa.Boolean(), nullable=False),
    sa.Column('workspace_level', sa.Boolean(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('type', sa.String(length=24), nullable=True),
    sa.ForeignKeyConstraint(['subscription_id'], ['notification_subscription.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subscription_id', 'type', name='uix_subscriptionid_type')
    )
    op.create_index(op.f('ix_notification_subscription_config_base_subscription_id'), 'notification_subscription_config_base', ['subscription_id'], unique=False)

    op.create_table('notification_subscription_mail_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('user_notified_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['notification_subscription_config_base.id'], ),
    sa.ForeignKeyConstraint(['user_notified_id'], ['faraday_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_subscription_mail_config_user_notified_id'), 'notification_subscription_mail_config', ['user_notified_id'], unique=False)
    op.create_table('notification_subscription_webhook_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['notification_subscription_config_base.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification_subscription_websocket_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_notified_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['notification_subscription_config_base.id'], ),
    sa.ForeignKeyConstraint(['user_notified_id'], ['faraday_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_subscription_websocket_config_user_notified_id'), 'notification_subscription_websocket_config', ['user_notified_id'], unique=False)

    op.create_table('notification_base',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('event_id', sa.Integer(), nullable=False),
                    sa.Column('notification_subscription_config_id', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=24), nullable=True),
                    sa.ForeignKeyConstraint(['event_id'], ['notification_event.id'], ),
                    sa.ForeignKeyConstraint(['notification_subscription_config_id'],
                                            ['notification_subscription_config_base.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_notification_base_event_id'), 'notification_base', ['event_id'], unique=False)
    op.create_index(op.f('ix_notification_base_notification_subscription_config_id'), 'notification_base',
                    ['notification_subscription_config_id'], unique=False)

    op.create_table('mail_notification',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['notification_base.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('webhook_notification',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['notification_base.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('websocket_notification',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_notified_id', sa.Integer(), nullable=True),
                    sa.Column('mark_read', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['notification_base.id'], ),
                    sa.ForeignKeyConstraint(['user_notified_id'], ['faraday_user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_websocket_notification_mark_read'), 'websocket_notification', ['mark_read'], unique=False)
    op.create_index(op.f('ix_websocket_notification_user_notified_id'), 'websocket_notification', ['user_notified_id'],
                    unique=False)

    # ### end Alembic commands ###

    # Added manually for inserts
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    from faraday.server.models import NotificationSubscription, NotificationSubscriptionWebSocketConfig,\
        NotificationRoles

    r1 = NotificationRoles(name='admin')
    r2 = NotificationRoles(name='pentester')
    r3 = NotificationRoles(name='client')
    r4 = NotificationRoles(name='asset_owner')

    n = NotificationSubscription(event='new_workspace', allowed_roles=[r1])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='update_workspace', allowed_roles=[r1])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='delete_workspace', allowed_roles=[r1])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='new_user', allowed_roles=[r1])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='update_user', allowed_roles=[r1])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='delete_user', allowed_roles=[r1])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='new_agent', allowed_roles=[r1, r2])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='update_agent', allowed_roles=[r1, r2])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='delete_agent', allowed_roles=[r1, r2])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='new_executivereport', allowed_roles=[r1, r2, r4])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='update_executivereport', allowed_roles=[r1, r2, r4])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='new_agentexecution', allowed_roles=[r1, r2, r4])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='new_command', allowed_roles=[r1, r2, r4])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='new_vulnerability', allowed_roles=[r1, r2, r3, r4])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='update_vulnerability', allowed_roles=[r1, r2, r3, r4])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='delete_vulnerability', allowed_roles=[r1, r2, r3, r4])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()

    n = NotificationSubscription(event='new_comment', allowed_roles=[r1, r2, r3, r4])
    session.add(n)
    session.commit()
    ns = NotificationSubscriptionWebSocketConfig(subscription=n, active=True, role_level=True)
    session.add(ns)
    session.commit()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_websocket_notification_user_notified_id'), table_name='websocket_notification')
    op.drop_index(op.f('ix_websocket_notification_mark_read'), table_name='websocket_notification')
    op.drop_table('websocket_notification')
    op.drop_table('webhook_notification')
    op.drop_table('mail_notification')
    op.drop_index(op.f('ix_notification_base_notification_subscription_config_id'), table_name='notification_base')
    op.drop_index(op.f('ix_notification_base_event_id'), table_name='notification_base')
    op.drop_table('notification_base')
    op.drop_index(op.f('ix_notification_subscription_websocket_config_user_notified_id'), table_name='notification_subscription_websocket_config')
    op.drop_table('notification_subscription_websocket_config')
    op.drop_table('notification_subscription_webhook_config')
    op.drop_index(op.f('ix_notification_subscription_mail_config_user_notified_id'), table_name='notification_subscription_mail_config')
    op.drop_table('notification_subscription_mail_config')
    op.drop_index(op.f('ix_notification_subscription_config_base_subscription_id'), table_name='notification_subscription_config_base')
    op.drop_table('notification_subscription_config_base')
    op.drop_table('notification_allowed_roles')
    op.drop_table('notification_subscription')
    op.drop_table('notification_event')
    op.drop_table('notification_roles')

    # Added Manually
    op.execute('DROP TYPE notification_events')
    ##

    # ### end Alembic commands ###
