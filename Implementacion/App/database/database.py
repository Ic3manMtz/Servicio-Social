from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Obtener connection string con validación
DATABASE_URL = os.getenv("DB_CONNECTION_STRING")

if not DATABASE_URL:
    raise ValueError(
        "No se encontró DB_CONNECTION_STRING en las variables de entorno. "
        "Por favor crea un archivo .env con esta variable."
    )

# Configurar el motor de SQLAlchemy
try:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )
    
    # Verificar la conexión
    with engine.connect() as test_conn:
        print("✅ Conexión a PostgreSQL establecida correctamente")
        
except Exception as e:
    print("❌ Error al conectar a la base de datos:")
    print(f"URL usada: {DATABASE_URL}")
    print(f"Error detallado: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()