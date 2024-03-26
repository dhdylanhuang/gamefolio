
$(document).ready(function() {

    const searchParams = new URLSearchParams(window.location.search);

    //Runs when any button is pressed
    $(".pagination-form").on("submit", function(e) {
        var $pageForm = $(this);
        //Get the number from the page input
        var pageSearch = $("#page-search");
        var number = pageSearch.val();
        var pageNumber = 0;
        //If theres no value dont use it
        if(number != null && number != "") {
            $("#page-parameter").remove();
            pageNumber = number;
        }

        //Get the current sort parameter
        var currentSort = "0"
        if(searchParams.has("sort")) {
            currentSort = searchParams.get("sort");
        }
        
        //If we have a valid page number and there isn't already a previous paramater add a page param
        if(pageNumber > 1 && !$("#page-parameter").length) {
            $('<input>').attr({
                type: 'hidden',
                value: pageNumber-1,
                name: "page",
                id: "page-parameter"
            }).appendTo($pageForm);
        }

        //If current sort isnt the default and there isn't already a previous paramater add a sort param
        if(currentSort != "0" && !$("#sort-parameter").length) {
            $('<input>').attr({
                type: 'hidden',
                value: currentSort,
                name: "sort",
                id: "sort-parameter"
            }).appendTo($pageForm);
        }
        //Get current query in URL parameter
        var query = ""
        if(searchParams.has("query") || $('#search-bar').val() != "") {
            query = $('#search-bar').val();
        }

        //If current query isnt the default and there isn't already a previous paramater add a query param
        if(!$("#query-parameter").length && query != "") {
            $('<input>').attr({
                type: 'hidden',
                value: query,
                name: "query",
                id: "query-parameter"
            }).appendTo($pageForm);
        }

        //If theres a genre search active and not a current param add a genre param
        if(searchParams.has('genre') &&  !$("#genre-parameter").length) {
            $('<input>').attr({
                type: 'hidden',
                value: searchParams.get('genre'),
                name: "genre",
                id: "genre-parameter"
            }).appendTo($pageForm);
        }

    })

    //For every numbered button at the bottom of page add this function on click
    var $pageButtons = jQuery('.number-button')
    $pageButtons.click(function(e) {
        var pageNumber = $(this).val();
        var $pageForm = $(this).parent().closest(".pagination-form");

        console.log($pageForm)

        //This function takes priority for page number
        $("#page-parameter").remove();
        $('<input>').attr({
            type: 'hidden',
            value: pageNumber-1,
            name: "page",
            id: "page-parameter"
        }).appendTo($pageForm);
    });

    //For every genre button add this function on click
    var $genreButtons = jQuery('.genre-button')
    $genreButtons.click(function(e) {
        $pageForm = $("#page-form");

        //This function takes priority for genre
        $("#genre-parameter").remove();
        if($(this).val() == "REMOVE") {
            $('<div>').attr({
                id: "genre-parameter"
            }).appendTo($pageForm);
            return;
        }
        $('<input>').attr({
            type: 'hidden',
            value: $(this).val(),
            name: "genre",
            id: "genre-parameter"
        }).appendTo($pageForm);
    })

    //For every sort button add this function on click
    var $sortButtons = jQuery('.sort-option')
    $sortButtons.click(function (e) {  

        var currentSort = $(this).val();
        $pageForm = $("#page-form");

        //When sort is called we want to keep the current search params apart from page
        //It is easier to clear all and start again
        $("#page-parameter").remove();
        $("#query-parameter").remove();
        $("#sort-parameter").remove();
        $("#genre-parameter").remove();
            
        if(currentSort != "0") {
            $('<input>').attr({
                type: 'hidden',
                value: currentSort,
                name: "sort",
                id: "sort-parameter"
            }).appendTo($pageForm);
        } else {
            //Prevents the form from adding the old sort param when relevance sort is picked
            $('<div>').attr({
                id: "sort-parameter"
            }).appendTo($pageForm);
        }
        
        if(searchParams.has('query')) {
            $('<input>').attr({
                type: 'hidden',
                value: searchParams.get('query'),
                name: "query",
                id: "query-parameter"
            }).appendTo($pageForm);
        }
        if(searchParams.has('genre')) {
            $('<input>').attr({
                type: 'hidden',
                value: searchParams.get('genre'),
                name: "genre",
                id: "genre-parameter"
            }).appendTo($pageForm);
        }
    })
});