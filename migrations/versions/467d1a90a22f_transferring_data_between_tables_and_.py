"""transferring data between tables and remaming

Revision ID: 467d1a90a22f
Revises: bb7d5dcf6e28
Create Date: 2024-07-11 12:49:28.866164

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '467d1a90a22f'
down_revision = 'bb7d5dcf6e28'
branch_labels = None
depends_on = None


def upgrade():
    # Transfer data from user to user2 where id = 7 (only the admin_tempoportal)
    op.execute("""
        INSERT INTO user2 (id, username, email, password, organization, auth_level, aligner, diffexp, qc_pages, ssg)
        SELECT id, username, email, password, organization, auth_level, aligner, diffexp, qc_pages, ssg
        FROM user
        WHERE id = 7
    """)

    # Deleting the current user table
    op.drop_table("user")

    # Renaming the user2 table to user
    op.execute("ALTER TABLE user2 RENAME TO user;")


def downgrade():
    # Reverting changes
    op.execute("ALTER TABLE user RENAME TO user2;")

    # Creating the table user 
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=128), nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.Column('organization', sa.String(length=128), nullable=False),
        sa.Column('auth_level', sa.String(length=128), nullable=False),
        sa.Column('aligner', sa.Boolean(), nullable=False),
        sa.Column('diffexp', sa.Boolean(), nullable=False),
        sa.Column('qc_pages', sa.Boolean(), nullable=False),
        sa.Column('ssg', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Transfer data back
    op.execute("""
        INSERT INTO user (id, username, email, password, organization, auth_level, aligner, diffexp, qc_pages, ssg)
        SELECT id, username, email, password, organization, auth_level, aligner, diffexp, qc_pages, ssg
        FROM user2
        WHERE id = 7
    """)
