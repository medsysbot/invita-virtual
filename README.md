# Tarjetas Invita Virtual — MVP (Flask + HTML + JS + Python)

## Requisitos
- Python 3.11+
- pip

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py  # inicializa DB y usuario admin: admin@example.com / admin123
flask --app app run --debug
```

## Credenciales
- Admin: admin@example.com / admin123
- Cliente de prueba: client@example.com / client123

## Notas
- DB: SQLite en `app.db`.
- Este MVP incluye: Público (Home/Tips), Login/Registro, Panel Cliente (DIY/Servicio completo), Panel Admin (Tips con flujo editorial, Planes, Solicitudes).
- Pagos: stub (sin integración con gateway).


## Despliegue en Railway (usando Supabase como DB)
1. Subir este repo a GitHub.
2. Crear proyecto en Supabase y obtener el `DATABASE_URI` (usar `?sslmode=require`).
3. En Railway: Deploy from GitHub → Variables:
   - `DATABASE_URI` = postgresql+psycopg://... (de Supabase)
   - `SECRET_KEY` = valor seguro
4. Railway detecta `Procfile` y ejecuta: `web: gunicorn app:app --bind 0.0.0.0:${PORT}`.
5. Primer arranque: crea el esquema automáticamente (SQLAlchemy).

## Alta de Admin (sin terminal)
- Regístrese desde la web y luego, en Supabase SQL Editor:
  ```sql
  update "user" set role = 'admin' where email = 'SU_EMAIL';
  ```


## Módulo Auth final
- Login cliente: /auth/login
- Registro cliente: /auth/register
- Login admin: /auth/admin-login
- Recuperación: /auth/forgot-password
- Reset: /auth/reset-password/<token>
- SQL único Supabase: `supabase_auth.sql`
