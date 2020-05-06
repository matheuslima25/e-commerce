jQuery(document).ready(function ($) {

    /*Login*/
    $("#login-btn").on("click", function (e) {
        let modalDiv = $("#login-div");
        e.preventDefault();
        $.ajax({
            type: "GET",
            url: $(this).attr("href"),
            data: {
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function (data) {
                modalDiv.html(data);
                $("#LoginModal").modal('show');
                $(".modal").on("hidden.bs.modal", function () {
                    $("#login-div").html("");
                });
            },
        });
    });

    $(document).on("submit", "#login-form", function (e) {
        e.preventDefault();
        let form = $(this);
        $.ajax({
            url: $(form).attr('action'),
            type: 'POST',
            dataType: 'json',
            data: $(form).serialize(),
            success: function (data, status, msg) {
                if (data.status) {
                    alert(data.msg);
                }
                window.location.reload();
            },
            error: function (data, status, error) {
                $('#login-errors').html('');
                $.each(data.responseJSON.error, function (i, val) {
                    $('#login-errors').append("<div class='alert alert-danger alert-dismissable'><a href='#'' class='close' data-dismiss='alert' aria-label='close'>×</a>" + val + "</div>");
                });
            }
        });
        return false;
    });

    /*Register*/
    $(document).on("click", '#register-btn', function (e) {
        let modalDiv = $("#registration-div");
        e.preventDefault();
        $.ajax({
            type: "GET",
            url: $(this).attr("href"),
            data: {
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function (data) {
                modalDiv.html(data);
                $("#RegisterModal").modal('show');
                $(".modal").on("hidden.bs.modal", function () {
                    $("#registration-div").html("");
                });
            },
        });
    });

    $(document).on("submit", "#register-form", function (e) {
        e.preventDefault();
        let form = $(this);
        $.ajax({
            url: $(form).attr('action'),
            type: 'POST',
            dataType: 'json',
            data: $(form).serialize(),
            success: function (data, status, msg) {
                if (data.status) {
                    alert(data.msg);
                }
                window.location.reload();
            },
            error: function (data, status, error) {
                $('#registration-errors').html('');
                console.log(data);
                $.each(data.responseJSON.error, function (i, val) {
                    $('#registration-errors').append("<div class='alert alert-danger alert-dismissable'><a href='#'' class='close' data-dismiss='alert' aria-label='close'>×</a>" + val + "</div>");
                });
            }
        });
        return false;
    });
});