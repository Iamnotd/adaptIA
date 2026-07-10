"""
modules/memory.py
Memoria persistente entre sesiones usando SQLite + SQLAlchemy.
Guarda cada interacción (transcripción, intención, resultado) con timestamp.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DB_PATH, MAX_CONTEXT_INTERACTIONS
from modules.logger import get_logger

logger = get_logger()

Base = declarative_base()


class Interaction(Base):
    """Tabla que guarda cada interacción del usuario con adaptIA."""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    transcripcion = Column(Text)
    intencion = Column(String(50))
    parametros = Column(Text)
    resultado = Column(Text)
    exitoso = Column(Integer, default=1)  # 1 = exitoso, 0 = fallido/cancelado


engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class MemoryManager:
    """Gestiona la lectura y escritura de la memoria persistente de adaptIA."""

    def __init__(self):
        self.session = Session()

    def guardar_interaccion(self, transcripcion, intencion, parametros, resultado, exitoso=True):
        """Guarda una nueva interacción en la base de datos."""
        try:
            nueva = Interaction(
                transcripcion=transcripcion,
                intencion=intencion,
                parametros=str(parametros),
                resultado=resultado,
                exitoso=1 if exitoso else 0
            )
            self.session.add(nueva)
            self.session.commit()
            logger.debug(f"Interacción guardada: {intencion}")
        except Exception as e:
            logger.exception(f"Error guardando interacción en memoria: {e}")
            self.session.rollback()

    def obtener_contexto_reciente(self, limite=MAX_CONTEXT_INTERACTIONS):
        """Devuelve las últimas N interacciones para dar contexto al LLM."""
        try:
            resultados = (
                self.session.query(Interaction)
                .order_by(Interaction.id.desc())
                .limit(limite)
                .all()
            )
            resultados.reverse()
            contexto = []
            for r in resultados:
                contexto.append({
                    "usuario": r.transcripcion,
                    "intencion": r.intencion,
                    "resultado": r.resultado
                })
            return contexto
        except Exception as e:
            logger.exception(f"Error obteniendo contexto de memoria: {e}")
            return []

    def cerrar(self):
        """Cierra la sesión de base de datos."""
        self.session.close()
