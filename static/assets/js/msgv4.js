
function GetMsg(val,id){
    document.getElementById('msgnewid').value=val
    if(document.getElementById('tekId'+val).value === '5825' || document.getElementById('tekId'+val).value === '613' ) {
   document.getElementById('refId').innerText ="مدیرسیستم";
        document.getElementById('sematId').innerText ="مدیرسیستم";
    }else{
        document.getElementById('refId').innerText =document.getElementById('refId'+val).value;
        document.getElementById('sematId').innerText =document.getElementById('sematId'+val).value;
    }
    document.getElementById('titelId').innerText =document.getElementById('titelId'+val).value;
    document.getElementById('imgId').innerText =document.getElementById('imgId'+val).value;
    document.getElementById('nameId').innerText =document.getElementById('nameId'+val).value;
    document.getElementById('infoId').innerText =document.getElementById('infoId'+val).value;
    document.getElementById('timeId').innerText =document.getElementById('timeId'+val).value;
    document.getElementById('msgidnew').value =id;
    // document.getElementById('attach').href =document.getElementById('attach'+val).value;
    const href1=document.getElementById('attach').href
    const last = href1.charAt(href1.length - 1);
    if (last === '0'){
        document.getElementById('attachfile').style.display = "none";
    }else{
        document.getElementById('attachfile').style.display = "block";
    }
    if (document.getElementById('isreply'+val).value === 'False') {
                document.getElementById('sendreply').style.display = "none";
    }else{
        document.getElementById('sendreply').style.display = "block";
    }
    if (document.getElementById('isread'+val).value === 'False') {


        $.ajax({
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                'id': id,
            },
            dataType: "json",
            url: '/msg/isRead/',
        }).done(function (data) {
            document.getElementById('IdRead' + id).classList.remove('active')

        });

    }
}


function Download() {
item = document.getElementById('msgnewid').value
     waiting();
    let url = '/api/showimgtek/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'id': item,
            'val': '4',
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var obj = 0;
         var link = document.createElement("a");
    // If you don't know the name or want to use
    // the webserver default set name = ''
    link.setAttribute('download', name);
    link.href = resp.ownerfiles;
    document.body.appendChild(link);
    link.click();
    link.remove();


        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1,error);
        });
    return false;

};
function getRole(id){
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'id': id,
        },
        dataType: "json",
        url: '/msg/getRole/',
    }).done(function (data) {
        $('#id_owners').empty()
        for (obj in data.mylist) {
            const mlist = data.mylist[obj]
            var content = '';
            content += '<option value=' + mlist.id + '>' + mlist.name + ' ' + mlist.lname + '</option>';
            $('#id_owners').append(content);

        }

    })
}

function testCo() {
        setTimeout(function () {
             if (document.getElementById('refreshBtn').style.display === "block") {
                 document.getElementById('cancelBtn').style.display = "block";
                 document.getElementById('refreshBtn').style.display = "none";
             }
        }, 6000)
}

function msgevenT(val) {
waiting();
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'val': val,

        },
        url: '/msg/msgevent/',
        dataType: "json",
        success: function (resp) {

            if (resp.message === "success") {

                $('#SerialTable tbody').empty()
                for (obj in resp.mylist) {
                    const mlist = resp.mylist[obj]
                    var content = '';
                    content += '<tr>'
                    content += '<td>' + mlist.name + '</td>'
                    content += '<td>' + mlist.status + '</td>'
                    content += '</tr>'
                    $('#SerialTable tbody').append(content);



                   ending();
                }
            }
        },
         error: function (xhr, status, error) {
            ending(1,error);
         }
    })
}