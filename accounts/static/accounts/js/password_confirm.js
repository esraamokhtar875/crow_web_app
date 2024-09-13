const form = document.getElementById('passwordResetForm');
const password1Input = document.getElementById('id_new_password1');
const password2Input = document.getElementById('id_new_password2');
const password1Error = document.getElementById('password1Error');
const password2Error = document.getElementById('password2Error');

form.addEventListener('submit', function (event) {
    if (!password1Input.value.trim()) {
        event.preventDefault();
        password1Error.classList.remove('d-none');
        password1Error.classList.add('d-block');
    }
    if (!password2Input.value.trim()) {
        event.preventDefault();
        password2Error.classList.remove('d-none');
        password2Error.classList.add('d-block');

    }
});

password1Input.classList.add('form-control');
password1Input.removeAttribute('required');
password1Input.addEventListener('input', function () {
    password1Error.classList.add('d-none');
});

password2Input.classList.add('form-control');
password2Input.removeAttribute('required');
password2Input.addEventListener('input', function () {
    password2Error.classList.add('d-none');
});
