$(document).ready(function () {
 
    $('#search_query').focus();

    let input = $('#search_query')[0];
    let length = input.value.length;
    input.setSelectionRange(length, length);
    input.focus();

    let checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function (checkbox) {

        let filter = checkbox.getAttribute('id');
        let t1 = 'label[for="';
        let t2 = filter;
        let t3 = '"]';
        let result = t1.concat(t2, t3);
        let label = document.querySelector(result);
        label.classList.add('unchecked');
        checkbox.removeAttribute('checked');

        checkbox.addEventListener('change', function () {
            if (label.classList.contains('unchecked')) {
                checkbox.setAttribute('checked', 'checked');
                label.classList.remove('unchecked');
                label.classList.add('checked');
            } else {
                label.classList.add('unchecked');
                label.classList.remove('checked');
                checkbox.removeAttribute('checked');
            }
        });
    });
});