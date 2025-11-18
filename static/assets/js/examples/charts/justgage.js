
$(document).ready(function () {

    var colors = {
        primary: $('.colors .bg-primary').css('background-color'),
        primaryLight: $('.colors .bg-primary-bright').css('background-color'),
        secondary: $('.colors .bg-secondary').css('background-color'),
        secondaryLight: $('.colors .bg-secondary-bright').css('background-color'),
        info: $('.colors .bg-info').css('background-color'),
        infoLight: $('.colors .bg-info-bright').css('background-color'),
        success: $('.colors .bg-success').css('background-color'),
        successLight: $('.colors .bg-success-bright').css('background-color'),
        danger: $('.colors .bg-danger').css('background-color'),
        dangerLight: $('.colors .bg-danger-bright').css('background-color'),
        warning: $('.colors .bg-warning').css('background-color'),
        warningLight: $('.colors .bg-warning-bright').css('background-color'),
    };

    var valueFontColor = "black";

    if($('body').hasClass('dark')){
        valueFontColor = "white";
    }

    function init() {



        var justgage_eight = new JustGage({
            id: "justgage_eight",
            value: 820,
            min: 0,
            max: 1000,
            label: "مصرف حافظه",
            pointer: true,
            pointerOptions: {
                toplength: -15,
                bottomlength: 10,
                bottomwidth: 12,
                color: colors.primary,
                stroke: colors.primary,
                stroke_width: 3,
                stroke_linecap: 'round'
            },
			valueFontColor: valueFontColor,
        });

        // Delete the extra added element when the page is resized.
        $('#justgage_eight > svg + svg').remove();

        var justgage_eight = new JustGage({
            id: "justgage_seven",
            value: 120,
            min: 0,
            max: 1000,
            label: "مصرف حافظه",
            pointer: true,
            pointerOptions: {
                toplength: -15,
                bottomlength: 10,
                bottomwidth: 12,
                color: colors.primary,
                stroke: colors.primary,
                stroke_width: 3,
                stroke_linecap: 'round'
            },
			valueFontColor: valueFontColor,
        });

        // Delete the extra added element when the page is resized.
        $('#justgage_eight > svg + svg').remove();


        setInterval(function () {
            justgage_seven.refresh(getRandomInt(0, 500));
            justgage_eight.refresh(getRandomInt(0, 500));

        }, 6000);
    }

init()

    $(window).on('resize', function () {
        init();
    });

});