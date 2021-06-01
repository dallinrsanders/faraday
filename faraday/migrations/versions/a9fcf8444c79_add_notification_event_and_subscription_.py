"""add_notification_event_and_subscription_model

Revision ID: a9fcf8444c79
Revises: a4def820a5bb
Create Date: 2021-05-28 15:47:13.781453+00:00

"""
from alembic import op
import sqlalchemy as sa
from faraday.server.fields import JSONType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a9fcf8444c79'
down_revision = 'a4def820a5bb'
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
    sa.PrimaryKeyConstraint('id')
    )

    ## Added manually
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
                              'agentexecution'
                              , name='object_types'),
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
    ## Added manually
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
                              'delete_comment'
                              , name='notification_events'),
                      nullable=False)
                  )

    ##

    op.create_table('notification_allowed_roles',
    sa.Column('notification_subscription_id', sa.Integer(), nullable=False),
    sa.Column('allowed_role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['allowed_role_id'], ['notification_roles.id'], ),
    sa.ForeignKeyConstraint(['notification_subscription_id'], ['notification_subscription.id'], )
    )


    op.create_table('notification_subscription_base_config',
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
    op.create_index(op.f('ix_notification_subscription_base_config_subscription_id'), 'notification_subscription_base_config', ['subscription_id'], unique=False)
    op.create_table('notification_sent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('notification_subscription_config_id', sa.Integer(), nullable=False),
    sa.Column('mark_read', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['notification_event.id'], ),
    sa.ForeignKeyConstraint(['notification_subscription_config_id'], ['notification_subscription_base_config.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_sent_event_id'), 'notification_sent', ['event_id'], unique=False)
    op.create_index(op.f('ix_notification_sent_mark_read'), 'notification_sent', ['mark_read'], unique=False)
    op.create_index(op.f('ix_notification_sent_notification_subscription_config_id'), 'notification_sent', ['notification_subscription_config_id'], unique=False)
    op.create_table('notification_subscription_mail_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('user_notified_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['notification_subscription_base_config.id'], ),
    sa.ForeignKeyConstraint(['user_notified_id'], ['faraday_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_subscription_mail_config_user_notified_id'), 'notification_subscription_mail_config', ['user_notified_id'], unique=False)
    op.create_table('notification_subscription_webhook_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['notification_subscription_base_config.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification_subscription_websocket_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_notified_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['notification_subscription_base_config.id'], ),
    sa.ForeignKeyConstraint(['user_notified_id'], ['faraday_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_subscription_websocket_config_user_notified_id'), 'notification_subscription_websocket_config', ['user_notified_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notification_subscription_websocket_config_user_notified_id'), table_name='notification_subscription_websocket_config')
    op.drop_table('notification_subscription_websocket_config')
    op.drop_table('notification_subscription_webhook_config')
    op.drop_index(op.f('ix_notification_subscription_mail_config_user_notified_id'), table_name='notification_subscription_mail_config')
    op.drop_table('notification_subscription_mail_config')
    op.drop_index(op.f('ix_notification_sent_notification_subscription_config_id'), table_name='notification_sent')
    op.drop_index(op.f('ix_notification_sent_mark_read'), table_name='notification_sent')
    op.drop_index(op.f('ix_notification_sent_event_id'), table_name='notification_sent')
    op.drop_table('notification_sent')
    op.drop_index(op.f('ix_notification_subscription_base_config_subscription_id'), table_name='notification_subscription_base_config')
    op.drop_table('notification_subscription_base_config')
    op.drop_table('notification_allowed_roles')
    op.drop_table('notification_subscription')
    op.drop_table('notification_event')
    op.drop_table('notification_roles')
    ## Added Manually
    op.execute('DROP TYPE notification_events')
    ##

    # ### end Alembic commands ###