const emailInput = document.getElementById('id_username');

emailInput.classList.add('form-control');
emailInput.removeAttribute('required');
emailInput.setAttribute('placeholder', 'Enter your email')
