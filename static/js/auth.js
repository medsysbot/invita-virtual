document.addEventListener('DOMContentLoaded', function () {
  const registerForm = document.querySelector('form[action$="/auth/register"]');
  if (registerForm) {
    registerForm.addEventListener('submit', function (event) {
      const password = registerForm.querySelector('input[name="password"]');
      const confirm = registerForm.querySelector('input[name="confirm_password"]');
      const terms = registerForm.querySelector('input[name="accept_terms"]');
      if (password && confirm && password.value !== confirm.value) {
        event.preventDefault();
        alert('Las contraseñas no coinciden.');
        return;
      }
      if (terms && !terms.checked) {
        event.preventDefault();
        alert('Debes aceptar los términos y condiciones.');
      }
    });
  }

  const resetForm = document.querySelector('form[action=""]') || document.querySelector('form:not([action])');
  if (resetForm && window.location.pathname.includes('/auth/reset-password/')) {
    resetForm.addEventListener('submit', function (event) {
      const password = resetForm.querySelector('input[name="new_password"]');
      const confirm = resetForm.querySelector('input[name="confirm_new_password"]');
      if (password && confirm && password.value !== confirm.value) {
        event.preventDefault();
        alert('Las contraseñas no coinciden.');
      }
    });
  }
});
