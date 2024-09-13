const spans = document.querySelectorAll('span');
spans.forEach(span => {
    span.classList.add('d-block');
});

const labels = document.querySelectorAll('label');
labels.forEach(label => {
    label.classList.add('form-label', 'my-3');
});

const inputs = document.querySelectorAll('input');
inputs.forEach(input => {
    input.classList.add('form-control');
    input.removeAttribute('required');
});

// const select = document.querySelector('select');
// select.classList.add('form-control');

const divs = document.querySelectorAll('.form_element');
divs.forEach(div => {
    div.classList.add('mb-3');
});

const checkboxes = document.querySelectorAll('input[type="checkbox"]');
checkboxes.forEach(checkbox => {
    checkbox.classList.remove('form-control');
});

const errors = document.querySelectorAll('ul.errorlist');

console.log(errors);

errors.forEach(error => {
    error.classList.add('text-danger', 'fw-bold');
});
