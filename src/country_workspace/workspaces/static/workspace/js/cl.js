$(function () {
    $("#result_list tbody tr").on("click", function () {
        var url = $(this).find("th a").attr("href");
        location.href = url;

    })
})
