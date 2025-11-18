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
                        resultsBox.innerHTML += `
<p>

                    <a href="/gs_detail/${result.pk}" class="text-warning d-block">
                        ${result.name}  ( ${result.gsid} )
                        <span class="text-success d-block"> ${result.nahye}</span></a>
                    <a href="/gs_detail/${result.pk}" class="badge badge-primary">اطلاعات جایگاه</a>
                    <a href="/CrudeTickets/?search=${result.pk}" class="badge badge-warning">تیکت های درحال بررسی</a>
                    </p>
                    `
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


searchInput.addEventListener('keyup', e=>{
    // console.log(e.target.value)
 if (e.target.value.length > 2){
    if (resultsBox.classList.contains('not-visible')){
        resultsBox.classList.remove('not-visible')    }

        sendSearchData(e.target.value)
 }
 else{
     resultsBox.innerHTML = ""
     resultsBox.classList.add('not-visible')
 }

})