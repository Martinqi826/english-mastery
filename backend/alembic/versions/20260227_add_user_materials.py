"""Add user materials tables

Revision ID: 20260227_materials
Revises: 
Create Date: 2026-02-27

添加用户自定义素材相关表：
- user_materials: 用户素材表
- generated_vocabularies: AI 生成的词汇表
- reading_questions: 阅读理解题目表
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260227_materials'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建用户素材表
    op.create_table(
        'user_materials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False, comment='素材标题'),
        sa.Column('source_type', sa.Enum('text', 'url', name='materialsourcetype'), nullable=False, comment='素材来源类型'),
        sa.Column('source_content', sa.Text(), nullable=False, comment='素材原文内容'),
        sa.Column('source_url', sa.String(length=1000), nullable=True, comment='来源URL'),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='materialstatus'), nullable=False, server_default='pending', comment='处理状态'),
        sa.Column('error_message', sa.String(length=500), nullable=True, comment='错误信息'),
        sa.Column('word_count', sa.Integer(), nullable=True, server_default='0', comment='单词数量'),
        sa.Column('generated_vocab_count', sa.Integer(), nullable=True, server_default='0', comment='生成的词汇数量'),
        sa.Column('generated_question_count', sa.Integer(), nullable=True, server_default='0', comment='生成的题目数量'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.Column('processed_at', sa.DateTime(), nullable=True, comment='处理完成时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_materials_id'), 'user_materials', ['id'], unique=False)
    op.create_index(op.f('ix_user_materials_user_id'), 'user_materials', ['user_id'], unique=False)

    # 创建生成词汇表
    op.create_table(
        'generated_vocabularies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('word', sa.String(length=100), nullable=False, comment='单词'),
        sa.Column('phonetic', sa.String(length=100), nullable=True, comment='音标'),
        sa.Column('translation', sa.String(length=500), nullable=False, comment='中文释义'),
        sa.Column('definition', sa.Text(), nullable=True, comment='英文释义'),
        sa.Column('example', sa.Text(), nullable=True, comment='例句'),
        sa.Column('example_translation', sa.Text(), nullable=True, comment='例句翻译'),
        sa.Column('synonyms', sa.JSON(), nullable=True, comment='同义词'),
        sa.Column('collocations', sa.JSON(), nullable=True, comment='常见搭配'),
        sa.Column('difficulty', sa.Integer(), nullable=True, server_default='3', comment='难度等级'),
        sa.Column('is_learned', sa.Boolean(), nullable=True, server_default='false', comment='是否已学习'),
        sa.Column('is_mastered', sa.Boolean(), nullable=True, server_default='false', comment='是否已掌握'),
        sa.Column('review_count', sa.Integer(), nullable=True, server_default='0', comment='复习次数'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0', comment='排序顺序'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['material_id'], ['user_materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generated_vocabularies_id'), 'generated_vocabularies', ['id'], unique=False)
    op.create_index(op.f('ix_generated_vocabularies_material_id'), 'generated_vocabularies', ['material_id'], unique=False)
    op.create_index(op.f('ix_generated_vocabularies_word'), 'generated_vocabularies', ['word'], unique=False)

    # 创建阅读理解题目表
    op.create_table(
        'reading_questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False, comment='题目内容'),
        sa.Column('question_type', sa.String(length=50), nullable=True, server_default='choice', comment='题目类型'),
        sa.Column('options', sa.JSON(), nullable=True, comment='选项列表'),
        sa.Column('correct_answer', sa.Integer(), nullable=False, comment='正确答案索引'),
        sa.Column('explanation', sa.Text(), nullable=True, comment='答案解析'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0', comment='排序顺序'),
        sa.Column('user_answer', sa.Integer(), nullable=True, comment='用户答案'),
        sa.Column('is_correct', sa.Boolean(), nullable=True, comment='是否回答正确'),
        sa.Column('answered_at', sa.DateTime(), nullable=True, comment='答题时间'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['material_id'], ['user_materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reading_questions_id'), 'reading_questions', ['id'], unique=False)
    op.create_index(op.f('ix_reading_questions_material_id'), 'reading_questions', ['material_id'], unique=False)


def downgrade() -> None:
    # 删除阅读理解题目表
    op.drop_index(op.f('ix_reading_questions_material_id'), table_name='reading_questions')
    op.drop_index(op.f('ix_reading_questions_id'), table_name='reading_questions')
    op.drop_table('reading_questions')
    
    # 删除生成词汇表
    op.drop_index(op.f('ix_generated_vocabularies_word'), table_name='generated_vocabularies')
    op.drop_index(op.f('ix_generated_vocabularies_material_id'), table_name='generated_vocabularies')
    op.drop_index(op.f('ix_generated_vocabularies_id'), table_name='generated_vocabularies')
    op.drop_table('generated_vocabularies')
    
    # 删除用户素材表
    op.drop_index(op.f('ix_user_materials_user_id'), table_name='user_materials')
    op.drop_index(op.f('ix_user_materials_id'), table_name='user_materials')
    op.drop_table('user_materials')
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS materialstatus")
    op.execute("DROP TYPE IF EXISTS materialsourcetype")
