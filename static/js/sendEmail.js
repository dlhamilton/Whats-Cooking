function sendMail(contactForm){
    emailjs.send("service_bfmxhch","template_5b6sesp", {
        "from_name": contactForm.name.value,
        "from_email": contactForm.emailaddress.value,
        "form_message": contactForm.formmessage.value,
    })
    .then(
        function(response){
            console.log("SUCCESS", response);
            let csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        
            fetch(`/aboutus/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf_token,
                    },
                    body: JSON.stringify({
                        'status': 1
                    })
                })
                .then((response) => response.json())
                .then((data) => {
    
                location.reload();
              
                })
        },
        function(error){
            console.log("FAILED", error);
            let csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        
            fetch(`/aboutus/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf_token,
                    },
                    body: JSON.stringify({
                        'status': 0
                    })
                })
                .then((response) => response.json())
                .then((data) => {
    
                location.reload();
              
                })
        }
    );
    return false;
}