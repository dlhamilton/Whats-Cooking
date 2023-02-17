let imModal = document.getElementById('im_staticBackdrop');
imModal.addEventListener('show.bs.modal', function (event) {
    let button = event.relatedTarget;
    let ingredients = button.getAttribute('data-bs-ingredient');
    let ingredients_id = button.getAttribute('data-bs-ingredient_id');
    let modalTitle = imModal.querySelector('.ingredient_modal .modal-title');
    let modalBodyInput = imModal.querySelector('.ingredient_modal .modal-body .ingredient_input input');
    
    modalTitle.textContent = ingredients;
    modalBodyInput.value = ingredients_id;
    document.getElementById("id_amount").value = "";
    document.getElementById("id_unit").selectedIndex = 0;
});

let rModal = document.getElementById('r_staticBackdrop')
rModal.addEventListener('show.bs.modal', function (event) {});

let mmModal = document.getElementById('mm_staticBackdrop')
mmModal.addEventListener('show.bs.modal', function (event) {
    let button = event.relatedTarget
    let methods_order = button.getAttribute('data-bs-method_order')
    let methods = button.getAttribute('data-bs-method')
    let methods_id = button.getAttribute('data-bs-method_id')
    let modalTitle = mmModal.querySelector('.method_modal .modal-title')
    let modalBodyInput = mmModal.querySelector('.method_modal .modal-body textarea')

    document.getElementById("the_method_form_id").value = methods_id;

    modalTitle.textContent = recipeTitle +" method - "+ methods_order;
    modalBodyInput.value = methods;
});

let remove_button = document.getElementById("remove-method");
if (remove_button){
  remove_button.addEventListener("click",  function(){removeIngredients(-1,"Methods")});
}

function removeIngredients(id,model) {
    if (id == -1){
      id = document.querySelector("#methods_section ul li:last-child").dataset.method_id;
    }
    let valid;
    let csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    fetch(fetchURL, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrf_token,
        },
        body: JSON.stringify({
          'id': id,
          'model': model
        })
    })
      .then(response => {
        if (response.ok) {
          valid = response;
          return response.json();
        }
        throw new Error(response.statusText);
    })
    .then(data => {
        console.log(data.message);
        console.log(valid);
        if (valid.ok) {
          if (model == "Methods"){
            let method = document.querySelector(`[data-method_id="${id}"]`);
            method.innerHTML = `<div class="alert alert-warning" role="alert">
                                This Method has been removed.
                                </div>`;
            setTimeout(function () {
                method.remove();
                if (data.last == 0){
                    location.reload();
                }
            }, 2500);
          }
          else{
            let comment = document.querySelector(`[data-comment_id="${id}"]`);
            comment.innerHTML = `<div class="alert alert-warning" role="alert">
                                This ingredient has been removed.
                                </div>`;
            setTimeout(function () {
                comment.remove();
            }, 2500);
          }
        } else {
          console.log(data.message);
        }
    })
    .catch(error => console.error(error));
}

if(goToIdIdBool){
    document.addEventListener("DOMContentLoaded", function() {
        let element = document.getElementById(goToIdId);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
}

let popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
});