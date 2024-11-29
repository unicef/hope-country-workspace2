$(function () {
    $("#tabs ul li button").on("click", function (){
        $("#tabs ul li button.selected").removeClass("selected");
        $(this).addClass("selected");
        $(this).data("selected");
        $("#tab-content div.content").addClass("hidden").hide();
        $($(this).data("tabs-target")).removeClass("hidden").show();
        $("input[name=_selected_tab]").val($(this).data("input-value"));
    });
})
