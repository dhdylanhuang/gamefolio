$(document).ready(function() {
    
    $("#search-bar").autocomplete({
        source: function(request, response) {
            var query;
            query = $("#search-bar").val();
            $.ajax({
                url: '/gamefolio/suggest/?suggestion='+query,
                success: function(data) {
                    response(JSON.parse(data)["games"])
                }
            });
        },
        select: function(event, ui) {
            $('#search-query-parameter').attr("value", ui.item.value);
            $("#search-bar").val(ui.item.value);
            $("#search-form").submit();
        },
        minLength: 0
    })
    $("#list-search-bar").autocomplete({
        source: function(request, response) {
            var query;
            query = $("#list-search-bar").val();
            $.ajax({
                url: '/gamefolio/suggest/?suggestion='+query,
                success: function(data) {
                    response(JSON.parse(data)["games"])
                }
            });
        },
        select: function(event, ui) {
            $.ajax({
                url: '/gamefolio/get-game/?id='+ui.item.id,
                success: function(data) {
                    $("#list-search-bar").val("");
                    if(!$("#" + ui.item.id).length) {
                        $("#list-games").append(data);
                    } else {
                        alert("Game already exists in list.")
                    }
                    return false;
                }
            })
        },
        minLength: 0
    })
    $("#list-games").on('mouseup', ".list-entry-remove-btn", function(e) {   
        $(this).parents("#list-entry").remove()
    });
    $("#list-games").on('mouseover', "#list-entry", function() {
        $(this).find(".list-entry-remove-btn").removeClass("d-none");
    });
    $("#list-games").on('mouseleave', "#list-entry", function() {
        $(this).find(".list-entry-remove-btn").addClass("d-none");
    });
    $("#list-form").keydown(function (e) {
        if(e.keyCode == 13){
            e.preventDefault();
        }
    })
})
$(document).ready(function() {
    $('.like-btn').click(function() {
        var reviewIdVar;
        reviewIdVar = $(this).attr('data-reviewid');
        var $t =$(this)

        $.get('/gamefolio/like_review/',
            {'review_id':reviewIdVar},
            function(data) {
                $t.hide();
                console.log($t.siblings())
                $t.siblings(".like-count").html(data +" likes");
            }
        );
    });
});

