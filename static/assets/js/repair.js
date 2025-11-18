
function validation_repair(){
        var tarikh = document.getElementById('id_tarikh_select').value
    if (tarikh.length === 0 ){
        alarm('warning','ابتدا تاریخ روز را انتخاب کنید')
        return false
    }else{
        $('#rform').submit()
    }
}
function repair_date(val) {
    waiting()
    var tarikh = document.getElementById('id_tarikh_select').value

    var newdate = tarikh.replace('/','-')
    newdate =newdate.replace('/','-')
    document.getElementById('id_tarikh').value = newdate
    $.ajax({
        type: 'GET',
        data: {
            'tarikh': tarikh,
            'store': val,
        },
        url: '/api/repairDate/',
        dataType: "json",
        success: function (resp) {

                $('#myTable tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    var content = '';
                    content += '<tr id=' + obj + '>'

                    content += '<td style="display: none" class="text-center">' + mlist.store_id + '</td>'
                    content += '<td  class="text-center">' + mlist.store + '</td>'
                    content += '<td class="text-center">' + mlist.svalue + '</td>'
                    content += '<td class="text-center text-danger"><a style="font-size: 25px" href="#" class="fa fa-trash-o text-danger"></a></td>'
                    $('#myTable tbody').append(content);
                    ending()
            }
        },
            error: function (xhr, status, error) {
            ending(1,error);
         }
    })
}