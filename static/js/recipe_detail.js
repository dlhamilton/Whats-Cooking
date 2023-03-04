if (isAuthenticated) {

    const form = document.querySelector('#myForm');
    let button = form.querySelector('.btn-like');
    let element = document.querySelector('#fav_count');
    let currentValue = parseInt(element.innerHTML, 10);
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(form);
        let recipe_slug = recipeSlug;
        let csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        fetch(`/recipes/${recipe_slug}/`, {
                method: 'POST',
                body: formData,
            })
            .then((response) => response.json())
            .then((data) => {
                // update the HTML page with the updated data
                if (data.liked) {
                    button.innerHTML = '<i class="fas fa-heart"></i>';
                    currentValue = currentValue + 1;
                    element.innerHTML = currentValue;
                } else {
                    button.innerHTML = '<i class="far fa-heart"></i>';
                    if (currentValue > 0) {
                        currentValue = currentValue - 1;
                    } else {
                        currentValue = currentValue;
                    }
                    element.innerHTML = currentValue;
                }
            })
            .then(() => {});
        return false;
    });
 }

    const checkbox = document.getElementById('flexSwitchCheckChecked');
    const comments_row = document.getElementById('comments_row');
    checkbox.addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            comments_row.style.display = 'flex';
        } else {
            comments_row.style.display = 'none';
        }
    });
    if (document.getElementById("image-main-carousel")) {
    var main = new Splide('#image-main-carousel', {
        gap: 20,
        rewind: true,
        perPage: 5,
        type: 'loop',
        autoplay: true,
        pagination: false,
        breakpoints: {
            500: {
                perPage: 1,
            },
            600: {
                perPage: 2,
            },
            750: {
                perPage: 3,
            },
            1000: {
                perPage: 4,
            }
        }
    }).mount();
    }

    function myFunction(id) {
        let valid;
        let recipe_slug = recipeSlug;
        let csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        fetch(`/recipes/${recipe_slug}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                },
                body: JSON.stringify({
                    'id': id,
                    'model': "comment"
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
                    //find the comment element
                    let comment = document.querySelector(`[data-comment_id="${id}"]`);
                    //remove the comment element from the comments section
                    comment.innerHTML = `<div class="alert alert-warning" role="alert">
  This comment has been removed.
</div>`;
                    setTimeout(function () {
                        comment.remove();
                    }, 2500);

                } else {
                    // Handle other status codes
                    console.log(data.message);
                }
            })
            .catch(error => console.error(error));
    }

    function removeImageFunction(id) {
        let valid;
        let recipe_slug = recipeSlug;
        let csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        fetch(`/recipes/${recipe_slug}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                },
                body: JSON.stringify({
                    'id': id,
                    'model': "image"
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
                location.reload();
            })
            .catch(error => console.error(error));
    }

    if (isAuthenticated) {
    $('.star_click').hover(function() {
  let num = $(this).data("num");
  $('.star_click[data-num]').each(function() {
    if ($(this).data("num") <= num) {
      $(this).css("color", "#ffc107");
      if ($(this).data("fill") == "clear") {
      $(this).addClass("fa-solid");
      $(this).removeClass("fa-regular");
      }
    }
  });
}, function() {
  $('.star_click[data-num]').css("color", "");
  
  $('.star_click[data-num]').each(function() {

  if ($(this).data("fill") == "clear") {
    $(this).removeClass("fa-solid");
    $(this).addClass("fa-regular");
  }

  if(ratedA){
    if ($(this).data("fill") != "clear") {
        $(this).css("color", "#667D36");
    }
 }
  });

});

$('.star_click').click( function(){
    event.preventDefault();
    let num = $(this).data("num")+1;

    document.getElementById("id_rating").value = num;
        let formDataRating = new FormData(the_rating_form_form);

        let recipe_slug = recipeSlug;
        let csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        
        fetch(`/recipes/${recipe_slug}/`, {
                method: 'POST',
                body: formDataRating,
            })
            .then((response) => response.json())
            .then((data) => {

            location.reload();
          
            })
            .then(() => {});
        return false;
});

}

document.getElementById("printButton").addEventListener("click", function() {
    window.print();
  });