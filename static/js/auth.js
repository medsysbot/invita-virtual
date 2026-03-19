(function () {
  const forms = document.querySelectorAll('[data-auth-validate]');
  if (!forms.length) return;

  document.querySelectorAll('[data-toggle-password]').forEach((button) => {
    button.addEventListener('click', () => {
      const target = document.querySelector(button.dataset.togglePassword);
      if (!target) return;
      const nextType = target.type === 'password' ? 'text' : 'password';
      target.type = nextType;
      button.textContent = nextType === 'password' ? 'Ver' : 'Ocultar';
    });
  });

  const rules = {
    login(form) {
      return checkRequired(form, ['email', 'password']);
    },
    'admin-login'(form) {
      return checkRequired(form, ['email', 'password']);
    },
    forgot(form) {
      return checkRequired(form, ['email']);
    },
    register(form) {
      if (!checkRequired(form, ['full_name', 'email', 'password', 'confirm_password'])) return false;
      const password = form.querySelector('[name="password"]').value.trim();
      const confirmPassword = form.querySelector('[name="confirm_password"]').value.trim();
      const accept = form.querySelector('[name="accept_terms"]');
      if (password.length < 8) return fail(form, 'La contraseña debe tener al menos 8 caracteres.');
      if (password !== confirmPassword) return fail(form, 'Las contraseñas no coinciden.');
      if (!accept || !accept.checked) return fail(form, 'Debes aceptar los términos y condiciones.');
      return ok(form);
    },
    reset(form) {
      if (!checkRequired(form, ['new_password', 'confirm_new_password'])) return false;
      const password = form.querySelector('[name="new_password"]').value.trim();
      const confirmPassword = form.querySelector('[name="confirm_new_password"]').value.trim();
      if (password.length < 8) return fail(form, 'La nueva contraseña debe tener al menos 8 caracteres.');
      if (password !== confirmPassword) return fail(form, 'Las contraseñas no coinciden.');
      return ok(form);
    }
  };

  forms.forEach((form) => {
    form.addEventListener('submit', (event) => {
      const mode = form.dataset.authValidate;
      const validator = rules[mode];
      if (validator && !validator(form)) {
        event.preventDefault();
      }
    });
  });

  function checkRequired(form, names) {
    for (const name of names) {
      const field = form.querySelector(`[name="${name}"]`);
      if (!field || !String(field.value || '').trim()) {
        return fail(form, 'Completa todos los campos obligatorios.');
      }
    }
    return ok(form);
  }

  function fail(form, message) {
    const box = form.querySelector('[data-form-error]');
    if (box) {
      box.textContent = message;
      box.classList.add('is-visible');
    }
    return false;
  }

  function ok(form) {
    const box = form.querySelector('[data-form-error]');
    if (box) {
      box.textContent = '';
      box.classList.remove('is-visible');
    }
    return true;
  }
})();
