"""
Servicio CRUD para Lineamientos
"""

from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from src.models.lineamiento import Lineamiento
from src.schemas.lineamiento import (
    LineamientoCreate,
    LineamientoUpdate,
)

logger = logging.getLogger(__name__)


class LineamientoService:
    """
    Servicio para operaciones CRUD de Lineamientos.
    Encapsula la lógica de negocio y acceso a datos.
    """

    @staticmethod
    def create(db: Session, lineamiento_data: LineamientoCreate) -> Lineamiento:
        """
        Crea un nuevo lineamiento.

        Args:
            db: Sesión de SQLAlchemy
            lineamiento_data: Datos para crear el lineamiento

        Returns:
            Lineamiento creado

        Raises:
            ValueError: Si ya existe un lineamiento con el mismo nombre
        """
        logger.info(f"Creando lineamiento: {lineamiento_data.nombre}")

        # Verificar si ya existe un lineamiento con el mismo nombre
        existing = (
            db.query(Lineamiento)
            .filter(Lineamiento.nombre == lineamiento_data.nombre)
            .first()
        )

        if existing:
            logger.warning(f"Lineamiento ya existe: {lineamiento_data.nombre}")
            raise ValueError(f"Ya existe un lineamiento con el nombre '{lineamiento_data.nombre}'")

        # Crear el lineamiento
        lineamiento = Lineamiento(
            nombre=lineamiento_data.nombre,
            keywords=lineamiento_data.keywords,
            plataformas=lineamiento_data.plataformas,
            activo=True,
        )

        try:
            db.add(lineamiento)
            db.commit()
            db.refresh(lineamiento)
            logger.info(f"Lineamiento creado: {lineamiento.id}")
            return lineamiento

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad al crear lineamiento: {e}")
            raise ValueError("Error al crear lineamiento: violación de restricción única")

    @staticmethod
    def get_by_id(db: Session, lineamiento_id: UUID) -> Lineamiento | None:
        """
        Obtiene un lineamiento por ID.

        Args:
            db: Sesión de SQLAlchemy
            lineamiento_id: ID del lineamiento

        Returns:
            Lineamiento si existe, None si no se encuentra
        """
        logger.debug(f"Buscando lineamiento: {lineamiento_id}")
        return db.query(Lineamiento).filter(Lineamiento.id == lineamiento_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        activo_only: bool = False,
    ) -> List[Lineamiento]:
        """
        Obtiene lista de lineamientos con paginación.

        Args:
            db: Sesión de SQLAlchemy
            skip: Número de registros a saltar (offset)
            limit: Número máximo de registros a retornar
            activo_only: Si True, solo retorna lineamientos activos

        Returns:
            Lista de lineamientos
        """
        logger.debug(f"Listando lineamientos: skip={skip}, limit={limit}, activo_only={activo_only}")

        query = db.query(Lineamiento)

        if activo_only:
            query = query.filter(Lineamiento.activo == True)

        return query.order_by(Lineamiento.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session, activo_only: bool = False) -> int:
        """
        Cuenta el total de lineamientos.

        Args:
            db: Sesión de SQLAlchemy
            activo_only: Si True, solo cuenta lineamientos activos

        Returns:
            Total de lineamientos
        """
        query = db.query(Lineamiento)

        if activo_only:
            query = query.filter(Lineamiento.activo == True)

        return query.count()

    @staticmethod
    def update(
        db: Session,
        lineamiento_id: UUID,
        lineamiento_data: LineamientoUpdate,
    ) -> Lineamiento | None:
        """
        Actualiza un lineamiento existente.

        Args:
            db: Sesión de SQLAlchemy
            lineamiento_id: ID del lineamiento a actualizar
            lineamiento_data: Datos a actualizar

        Returns:
            Lineamiento actualizado, o None si no se encuentra

        Raises:
            ValueError: Si el nuevo nombre ya existe en otro lineamiento
        """
        logger.info(f"Actualizando lineamiento: {lineamiento_id}")

        # Obtener el lineamiento existente
        lineamiento = LineamientoService.get_by_id(db, lineamiento_id)

        if not lineamiento:
            logger.warning(f"Lineamiento no encontrado: {lineamiento_id}")
            return None

        # Preparar datos a actualizar (solo campos no-None)
        update_data = lineamiento_data.model_dump(exclude_unset=True)

        # Si se está actualizando el nombre, verificar que no exista otro con ese nombre
        if "nombre" in update_data and update_data["nombre"] != lineamiento.nombre:
            existing = (
                db.query(Lineamiento)
                .filter(
                    Lineamiento.nombre == update_data["nombre"],
                    Lineamiento.id != lineamiento_id,
                )
                .first()
            )

            if existing:
                logger.warning(f"Nombre ya existe: {update_data['nombre']}")
                raise ValueError(f"Ya existe un lineamiento con el nombre '{update_data['nombre']}'")

        # Actualizar campos
        for field, value in update_data.items():
            setattr(lineamiento, field, value)

        try:
            db.commit()
            db.refresh(lineamiento)
            logger.info(f"Lineamiento actualizado: {lineamiento.id}")
            return lineamiento

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad al actualizar lineamiento: {e}")
            raise ValueError("Error al actualizar lineamiento: violación de restricción única")

    @staticmethod
    def delete(db: Session, lineamiento_id: UUID) -> bool:
        """
        Elimina un lineamiento (soft delete - marca como inactivo).

        Args:
            db: Sesión de SQLAlchemy
            lineamiento_id: ID del lineamiento a eliminar

        Returns:
            True si se eliminó, False si no se encontró
        """
        logger.info(f"Eliminando lineamiento: {lineamiento_id}")

        lineamiento = LineamientoService.get_by_id(db, lineamiento_id)

        if not lineamiento:
            logger.warning(f"Lineamiento no encontrado: {lineamiento_id}")
            return False

        # Soft delete: marcar como inactivo
        lineamiento.activo = False

        db.commit()
        logger.info(f"Lineamiento marcado como inactivo: {lineamiento.id}")
        return True

    @staticmethod
    def hard_delete(db: Session, lineamiento_id: UUID) -> bool:
        """
        Elimina permanentemente un lineamiento de la base de datos.

        ADVERTENCIA: Esta operación es irreversible y eliminará
        también todo el contenido recolectado asociado (CASCADE).

        Args:
            db: Sesión de SQLAlchemy
            lineamiento_id: ID del lineamiento a eliminar

        Returns:
            True si se eliminó, False si no se encontró
        """
        logger.warning(f"HARD DELETE de lineamiento: {lineamiento_id}")

        lineamiento = LineamientoService.get_by_id(db, lineamiento_id)

        if not lineamiento:
            logger.warning(f"Lineamiento no encontrado: {lineamiento_id}")
            return False

        db.delete(lineamiento)
        db.commit()
        logger.info(f"Lineamiento eliminado permanentemente: {lineamiento_id}")
        return True

    @staticmethod
    def activate(db: Session, lineamiento_id: UUID) -> Lineamiento | None:
        """
        Reactiva un lineamiento inactivo.

        Args:
            db: Sesión de SQLAlchemy
            lineamiento_id: ID del lineamiento a activar

        Returns:
            Lineamiento activado, o None si no se encuentra
        """
        logger.info(f"Activando lineamiento: {lineamiento_id}")

        lineamiento = LineamientoService.get_by_id(db, lineamiento_id)

        if not lineamiento:
            logger.warning(f"Lineamiento no encontrado: {lineamiento_id}")
            return None

        lineamiento.activo = True
        db.commit()
        db.refresh(lineamiento)
        logger.info(f"Lineamiento activado: {lineamiento.id}")
        return lineamiento
