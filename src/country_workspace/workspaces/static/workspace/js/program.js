$(function () {
    $("#result_list tbody tr td.field").on("click", function () {
        var url = $(this).parent().find("th a").attr("href");
        location.href = url;
    })


})
