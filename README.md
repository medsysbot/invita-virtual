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
1. Regístrese desde la web con `/auth/register`.
2. Luego, en Supabase SQL Editor, ejecute:
  ```sql
  update public."user"
  set role = 'admin', is_active = true
  where email = 'SU_EMAIL';
  ```
3. Ingrese por `/auth/login`. Si el rol es `admin`, el sistema redirige automáticamente a `/admin`.


## Módulo Auth final
- Login único: /auth/login
- Registro cliente: /auth/register
- Recuperación: /auth/forgot-password
- Reset: /auth/reset-password/<token>
- Promoción admin por SQL: `supabase_promote_admin.sql`
- SQL base Supabase: `supabase_full_schema.sql`


## Módulos funcionales cerrados
- Auth completo: login único por rol, registro cliente, recuperar y resetear contraseña.
- Cliente: crear invitación, vista previa, checkout, pedido y pago demo.
- Admin: usuarios, crear admin, detalle de usuario, pedidos, invitaciones y solicitudes.
