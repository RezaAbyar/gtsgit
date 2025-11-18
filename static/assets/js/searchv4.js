const url = '/api/search/'
const searchForm = document.getElementById('search-form')
const searchInput = document.getElementById('search-input')
const resultsBox = document.getElementById('results-box')
const sendSearchData = (result) => {

    $.ajax({
        type: 'GET',
        url: url,
        data: {
            'result': searchInput.value,
        },
        success: (res) => {
            // console.log(res)
            const data = res.data
            if (Array.isArray(data)) {
                resultsBox.innerHTML = ""
                data.forEach(result => {
                    if (res.st === 'gs') {
                        resultsBox.innerHTML += `
                    <p>

                    <a href="/gs_detail/${result.pk}" class="text-warning d-block">
                        ${result.name}  ( ${result.gsid} )
                        <span class="text-success d-block"> ${result.nahye}</span></a>
                        <label class="badge badge-${result.status_code}">${result.status}</label>
                    <a style="color: #fff6f8" href="/gs_detail/${result.pk}" class="badge badge-primary">اطلاعات جایگاه</a>
                    <a href="/CrudeTickets/?search=${result.gsid}" class="badge badge-warning">تیکت های درحال بررسی</a>
                    <a href="/reportipc/?search=${result.gsid}" class="badge badge-info">وضعیت سرور</a>
                    
                    <a style="color: #fff6f8"  href="#" onclick="goaddress(${result.pk})" class="badge badge-secondary"> آدرس و تلفن جایگاه</a>
                    </p>
                    `
                    }
                     if (res.st === 'owner') {
                        resultsBox.innerHTML += `
                    <p>

                    <a  class="text-warning d-block">
                        ${result.name} ( ${result.mobail} - ${result.codemeli} )
                        <span class="text-success d-block"> ${result.nahye}</span></a>
                         <label class="badge badge-${result.status_code}">${result.active}</label>               
                         <textarea style="font-size: 13px" disabled class="form-control badge badge-warning">${result._gslist}</textarea>                
                    </p>
                    `
                    }
                      if (res.st === 'ticket') {
                        resultsBox.innerHTML += `
                    <p>

                    <a  class="text-warning d-block">
                        ${result.gsid} ( ${result.name})
                        <span class="text-success d-block"> ${result.nahye}</span></a>
                        <a href="/RoleTickets/?search=${result.pk}" class="badge badge-primary">مشاهده تیکت</a>

                    </p>
                    `
                    }

                })

            } else {
                if (searchInput.value.length > 0) {
                    resultsBox.innerHTML = `<b>${data}</b>`
                } else {
                    resultsBox.classList.add('not-visible')
                }
            }

        },
        error: (err) => {
            console.log(err)
        }
    })

}


searchInput.addEventListener('keyup', e => {
    // console.log(e.target.value)
    if (e.target.value.length > 2) {
        if (resultsBox.classList.contains('not-visible')) {
            resultsBox.classList.remove('not-visible')
        }

        sendSearchData(e.target.value)
    } else {
        resultsBox.innerHTML = ""
        resultsBox.classList.add('not-visible')
    }

})

function goaddress(gsid){

     waiting();
    let url = '/api/goaddress/'

    $.ajax({
        type: 'GET',
        data: {

            'gsid': gsid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {

        swal({
            title: resp.name,
            text:
                ' نام جایگاه: ' + resp.name + " " +
                '\n' +
                ' نام ناحیه: ' + resp.area + " " +
                '\n' +
                ' نام منطقه: ' + resp.zone + " " +
                '\n' +
                ' تلفن دفتر: ' + resp.tell + " " +
                '\n' +
                '  آدرس: ' +resp.address + " "



            ,

            icon: "info",
            confirmButtonText: 'بستن',


        })
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });

}