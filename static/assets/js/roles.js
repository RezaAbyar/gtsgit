

function listRole() {

    $.ajax({
        type: 'GET',
        data: {
        },
        url:'/getRoles/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === 'success'){
                 var content = '';
                 var obj =1


                 $('#id_role').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    if (resp.n_role === mlist.id) {
                        content += '<option selected value=' + mlist.id + '>' + mlist.name + '</option>'
                    } else {
                        content += '<option value=' + mlist.id + '>' + mlist.name + '</option>'
                    }
                }
                $('#id_role').append(content)

                            content = '';
                  obj =1;
                 $('#id_sematrole').empty()
                for (obj in resp.semat) {
                    const mlist = resp.semat[obj]
                    if (resp.n_semat === mlist.id) {
                        content += '<option selected value=' + mlist.id + '>' + mlist.name + '</option>'
                    } else {
                        content += '<option value=' + mlist.id + '>' + mlist.name + '</option>'
                    }
                }
                $('#id_sematrole').append(content)

                            content = '';
                  obj =1;

                 $('#id_zonerole').empty()
                for (obj in resp.zlist) {
                    const mlist = resp.zlist[obj]
                    if (resp.n_zone === mlist.id) {

                        content += '<option selected value=' + mlist.id + '>' + mlist.name + '</option>'
                    } else {
                        content += '<option value=' + mlist.id + '>' + mlist.name + '</option>'
                    }
                }
                $('#id_zonerole').append(content)

            }
        }
    })
}