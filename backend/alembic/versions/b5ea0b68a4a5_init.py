"""init

Revision ID: b5ea0b68a4a5
Revises: 
Create Date: 2026-07-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'b5ea0b68a4a5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create Postgres enums
    # Create enums only if missing (safe for existing DBs)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_sync') THEN
            CREATE TYPE estado_sync AS ENUM ('pending','running','completed','failed','rejected');
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_archivo') THEN
            CREATE TYPE tipo_archivo AS ENUM ('ventas','inventario','clientes');
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'nivel_error') THEN
            CREATE TYPE nivel_error AS ENUM ('WARNING','ERROR','CRITICAL');
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'resultado_accion') THEN
            CREATE TYPE resultado_accion AS ENUM ('success','failed');
        END IF;
    END$$;
    """)

    # Create tables
    op.create_table(
        'sincronizaciones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('correlation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fecha_ejecucion', sa.Date(), nullable=False),
        sa.Column('estado', postgresql.ENUM('pending','running','completed','failed','rejected', name='estado_sync', create_type=False), nullable=False),
        sa.Column('iniciado_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('finalizado_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('usuario_origen', sa.String(length=100), nullable=True),
    )
    op.create_index('ix_sincronizaciones_correlation_id', 'sincronizaciones', ['correlation_id'], unique=True)

    op.create_table(
        'archivos_procesados',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sincronizacion_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sincronizaciones.id', ondelete='CASCADE')),
        sa.Column('nombre_archivo', sa.String(length=255), nullable=False),
        sa.Column('tipo_archivo', postgresql.ENUM('ventas','inventario','clientes', name='tipo_archivo', create_type=False), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=True),
        sa.Column('registros_totales', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('datos_payload', postgresql.JSONB(), nullable=True),
    )
    op.create_index('ix_archivos_procesados_checksum', 'archivos_procesados', ['checksum'], unique=True)

    op.create_table(
        'logs_errores',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('correlation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sincronizaciones.correlation_id', ondelete='CASCADE')),
        sa.Column('servicio_responsable', sa.String(length=100), nullable=True),
        sa.Column('nivel_error', postgresql.ENUM('WARNING','ERROR','CRITICAL', name='nivel_error', create_type=False), nullable=True),
        sa.Column('codigo_error', sa.String(length=50), nullable=True),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('creado_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
    )
    op.create_index('ix_logs_errores_correlation_id', 'logs_errores', ['correlation_id'])

    op.create_table(
        'acciones_remediacion',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sincronizacion_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sincronizaciones.id', ondelete='CASCADE')),
        sa.Column('accion_ejecutada', sa.String(length=100), nullable=True),
        sa.Column('ejecutado_por', sa.String(length=100), nullable=False),
        sa.Column('resultado', postgresql.ENUM('success','failed', name='resultado_accion', create_type=False), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table('acciones_remediacion')
    op.drop_index('ix_logs_errores_correlation_id', table_name='logs_errores')
    op.drop_table('logs_errores')
    op.drop_index('ix_archivos_procesados_checksum', table_name='archivos_procesados')
    op.drop_table('archivos_procesados')
    op.drop_index('ix_sincronizaciones_correlation_id', table_name='sincronizaciones')
    op.drop_table('sincronizaciones')

    resultado_accion = postgresql.ENUM(name='resultado_accion')
    resultado_accion.drop(op.get_bind(), checkfirst=True)

    nivel_error = postgresql.ENUM(name='nivel_error')
    nivel_error.drop(op.get_bind(), checkfirst=True)

    tipo_archivo = postgresql.ENUM(name='tipo_archivo')
    tipo_archivo.drop(op.get_bind(), checkfirst=True)

    estado_sync = postgresql.ENUM(name='estado_sync')
    estado_sync.drop(op.get_bind(), checkfirst=True)
