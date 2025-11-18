function getArzyabiitems(){
    var period = document.getElementById('period_id').value
    var base_group_id = document.getElementById('group_id').value

 $.ajax({
        type: 'GET',
        data: {
            'base_group_id': base_group_id,
            'period': period,
        },
        dataType: "json",
        url: '/api/get-arzyabi-item/',
    }).done(function (data) {
        $('#tblList tbody').empty()
        for (obj in data.mylist) {

            const mlist = data.mylist[obj]
            var content = '';
            content += '<tr>'
            content += '<td> mlist.name </td>'

            content += '</td>'
            content += '</tr>'

            $('#tblList tbody').append(content);

        }
    })

}