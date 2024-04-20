window.addEventListener( "pageshow", function ( event ) {
    var historyTraversal = event.persisted || 
                           ( typeof window.performance != "undefined" && 
                                window.performance.navigation.type === 2 );
    if ( historyTraversal ) {
      // Handle page restore.
      window.location.reload();
    }
  });
  
  
  $(document).ready(function() {
  
      const searchParams = new URLSearchParams(window.location.search);
      var ratingConfirmed = false;
      
      $('#search-form').submit(function(e) {
          var queryTerm = $('#search-bar').val();
          if($('#search-query-parameter').val() == ""){
              $('#search-query-parameter').attr("value", queryTerm);
          }
          if($('#page-form').length) {
              $('#page-form').trigger("submit");
          }
      });
      $('#reset-button').click(function(e) {
          $('#search-bar').val("");
          if($('#page-form').length && searchParams.has("query")) {
              $('#page-form').trigger("submit");
          } else {
              e.preventDefault();
          }
      });
  
      $(".list-selection-dropdown").click(function(e) {
          $("#add-to-list-button").val($(this).val());
      })
  
      $("#add-to-list-button").click(function(e) {
          window.location.href = "../../add_to_list_form/"+$(this).val()+"/"+$("#game-slug").val()
      })
  
      $("#edit-button").click(function(e) {
          $("#edit-profile-form").removeClass("d-none");
          $("#non-edit-profile").addClass("d-none");
      })
  
      //Ratings
      function calculateSize(e) {
          var rating = calculateRating(e);
          var width = $("#rating-input").width();
          const halfStarSize = width/10;
          var newWidth = width * (rating/10);
          var newWidth = newWidth - (newWidth % halfStarSize)
  
          return newWidth;
      }
  
      function calculateRating(e) {
          var mouseX = e.pageX;
          var left = $("#rating-hover").offset().left;
          var width = $("#rating-input").width();
          var relativeMouseX = mouseX-left;
          var percentage = relativeMouseX/width + 0.095;
          if(percentage < 0.1) {
              percentage = 0.1;
          }
          return Math.floor(10*percentage);
      }
      $('#rating-input').mousemove(function(e) {
          $("#rating-actual").addClass("d-none");
          $("#rating-hover").get(0).style.setProperty("--width", calculateSize(e)+"px");
      });
      
      $('#rating-input').mouseleave(function(e) {
          $("#rating-actual").removeClass("d-none");
          $("#rating-hover").get(0).style.setProperty("--width", "0px");
      });
  
      $('#rating-input').click(function(e) {
          $("#rating-actual").removeClass("d-none");
          $("#id_rating").attr("value", calculateRating(e));
          $("#rating-actual").get(0).style.setProperty("--width", calculateSize(e) + "px");
          $("#rating-hover").get(0).style.setProperty("--width", "0px");
      });
  
      const reviewsPerPage = 6;
      var currentReviewPage = 1;
      var currentReviews= Array.from(Array(reviewsPerPage).keys())
      var maxReviewPage = Math.ceil($(".user-review").toArray().length/reviewsPerPage);
      paginateReviews();
  
      function paginateReviews() {
          const userReviews = $(".user-review").each(function(i, el) {
              if(!currentReviews.includes(i)) {
                  $(this).addClass("d-none");
              } else {
                  $(this).removeClass("d-none");
              }
          })
          $("#current-review-page").text(currentReviewPage.toString().concat("/").concat(maxReviewPage.toString()));
          $("#prev-review-button").removeClass("disabled");
          $("#next-review-button").removeClass("disabled");
          
          if(currentReviewPage == 1) {
              $("#prev-review-button").addClass("disabled");
          }
          if(currentReviewPage >= maxReviewPage) {
              $("#next-review-button").addClass("disabled");
          }
          if(maxReviewPage <= 1) {
              $("#prev-list-button").addClass("d-none");
              $("#next-list-button").addClass("d-none");
              $("#current-list-page").addClass("d-none");
  
          }
      }
  
      $("#next-review-button").click(function() {
          currentReviewPage++
          for (let i = 0; i < currentReviews.length; i++) {
              currentReviews[i] += reviewsPerPage;
          }
          paginateReviews();
      })
  
      $("#prev-review-button").click(function() {
          currentReviewPage--;
          for (let i = 0; i < currentReviews.length; i++) {
              currentReviews[i] -= reviewsPerPage;
          }
          paginateReviews();
      })
  
      const listsPerPage =3;
      var currentListPage = 1;
      var currentLists = Array.from(Array(listsPerPage).keys())
      var maxListPage = Math.ceil($(".user-list").toArray().length/listsPerPage);
      paginateLists();
  
      function paginateLists() {
          const userLists = $(".user-list").each(function(i, el) {
              if(!currentLists.includes(i)) {
                  $(this).addClass("d-none");
              } else {
                  $(this).removeClass("d-none");
              }
          })
          $("#current-list-page").text(currentListPage.toString().concat("/").concat(maxListPage.toString()));
          $("#prev-list-button").removeClass("disabled");
          $("#next-list-button").removeClass("disabled");
          
          if(currentListPage == 1) {
              $("#prev-list-button").addClass("disabled");
          }
          if(currentListPage >= maxListPage) {
              $("#next-list-button").addClass("disabled");
          }
  
          if(maxListPage <= 1) {
              $("#prev-list-button").addClass("d-none");
              $("#next-list-button").addClass("d-none");
              $("#current-list-page").addClass("d-none");
  
          }
      }
  
      $("#next-list-button").click(function() {
          currentListPage++
          for (let i = 0; i < currentLists.length; i++) {
              currentLists[i] += listsPerPage;
          }
          paginateLists();
      })
  
      $("#prev-list-button").click(function() {
          currentListPage--;
          for (let i = 0; i < currentLists.length; i++) {
              currentLists[i] -= listsPerPage;
          }
          paginateLists();
      })
  
      $("#profile-image").click(function() {
          $("#id_picture").trigger("click");
      })
  
      $("#id_picture").change(function() {
          $("#edit-profile-form").trigger("submit");
      })
  
      //Tooltips
      const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
      const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
  });
  
  document.getElementById('privacy-button').addEventListener('click', function(event) {
      event.preventDefault();
      alert('We make use of cookies to only store the most basic of data, none of which is shared with third parties.');
  });
  
  document.getElementById('terms-button').addEventListener('click', function(event) {
      event.preventDefault();
      alert('By using this website, you agree to the terms and conditions set out by the University Of Glasgow.');
  });
  
  document.getElementById('contact-button').addEventListener('click', function(event) {
      event.preventDefault();
      alert('Contact us at: 2789356h@student.gla.ac.uk or phone us at: 07909 916 436.');
  });
  