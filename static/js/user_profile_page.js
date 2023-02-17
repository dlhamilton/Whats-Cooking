let splide_settings = {
    type: 'loop',
    perPage: 3,
    drag: 'free',
    breakpoints: {
      1020: {
        perPage: 2,
        gap: '.7rem',
      },
      700: {
        perPage: 1,
        gap: '.7rem',
      },
    },
  }

  let splide_settings_big = {
    type: 'loop',
    perPage: 4,
    drag: 'free',
    breakpoints: {
      1300: {
        perPage: 3,
        gap: '1rem',
      },
      990: {
        perPage: 2,
        gap: '1rem',
      },
      500: {
        perPage: 1,
        gap: '1rem',
      },
    },
  }

  if (document.getElementById("splide1")) {
  var splide1 = new Splide('#splide1', splide_settings);
  splide1.mount();
  }
  if (document.getElementById("splide2")) {
  var splide2 = new Splide('#splide2', splide_settings_big);
  splide2.mount();
  }
  if (document.getElementById("splide3")) {
  var splide3 = new Splide('#splide3', splide_settings_big);
  splide3.mount();
  }

  $("#following_id").hover(function(){
  $(this).attr("value", "Unfollow");
}, function(){
  $(this).attr("value", "Following");
});