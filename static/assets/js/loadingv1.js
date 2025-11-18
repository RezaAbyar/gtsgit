function loading(objerr, infoerr) {

            toastr.options = {
                timeOut: 0,
                progressBar: false,
                showMethod: "slideDown",
                hideMethod: "slideUp",
                showDuration: 50,
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
                       if (objerr === 'loading') {
                toastr.loading(infoerr);
            }

}


function waiting(){
  loading('loading','لطفا صبر کنید ، در حال پردازش عملیات')


}

function ending(val,err='0'){
    if (val===1){
         alarm('error', 'خطایی رخ داده است'+err);
    }

toastr.clear();
}

