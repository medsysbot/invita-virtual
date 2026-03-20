-- Registra primero el usuario desde /auth/register y luego ejecútalo aquí.
update public."user"
set
    role = 'admin',
    is_active = true
where email = 'tuemail@dominio.com';

select id, full_name, email, role, is_active
from public."user"
where email = 'tuemail@dominio.com';
