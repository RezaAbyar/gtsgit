  $('form').on('submit', function() {
   $(this).find(":submit").prop('disabled', true);

 });
function alarm(objerr, infoerr) {
    $('.preloader2').fadeOut(700, function () {
        setTimeout(function () {
            toastr.options = {
                timeOut: 5000,
                progressBar: true,
                showMethod: "slideDown",
                hideMethod: "slideUp",
                showDuration: 200,
                hideDuration: 200
            };

            if (objerr === 'info') {
                toastr.info(infoerr);
            }

            if (objerr === 'warning') {
                toastr.warning(infoerr);
            }
            if (objerr === 'success') {
                toastr.success(infoerr);
            }

            if (objerr === 'danger') {
                toastr.error(infoerr);
            }
            if (objerr === 'error') {
                toastr.error(infoerr);
            }
            $('.theme-switcher').removeClass('open');
        }, 500);

        $('.theme-switcher').css('opacity', 1);
    });
}


// function waiting(){
//       document.getElementById('cnBtn').style.display = "none";
//   document.getElementById('refreshBtn').style.display = "block";
//
// }
//
// function ending(val){
//
//     if (val===1){
//          alarm('error', 'خطایی رخ داده است');
//     }
//
//   document.getElementById('refreshBtn').style.display = "none";
//   document.getElementById('cnBtn').style.display = "block";
// }

