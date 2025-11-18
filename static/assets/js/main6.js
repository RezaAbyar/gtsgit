const Mylad = document.getElementById('Mylad')
const AreaZone = document.getElementById('Master')
const selectRole = document.getElementById('selectRole')
const userSave = document.getElementById('userSave')
const zoneId = document.getElementById('zoneid')
const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value



Mylad.addEventListener('change', e => {
 waiting();
    id = Mylad.value

    document.getElementById('userZone').style.display = "none";
    document.getElementById('userArea').style.display = "none";
    document.getElementById('userStorage').style.display = "none";
    if (zoneid.value==='0') {
        if (id === '4') {
            document.getElementById('userZone').style.display = "block";
            document.getElementById('userArea').style.display = "block";
        }
                if (id === '1') {
            document.getElementById('userZone').style.display = "block";
            document.getElementById('userArea').style.display = "block";
        }
        if (id === '2') {
            document.getElementById('userZone').style.display = "block";
        }
          if (id === '11') {
            document.getElementById('userStorage').style.display = "block";
        }
         if (id === '102') {
            document.getElementById('userZone').style.display = "block";
        }
        if (id === '3') {
            document.getElementById('userZone').style.display = "block";
        }
        if (id === '5') {
            document.getElementById('userZone').style.display = "block";
        }
    }else{
         if (id === '4') {

            document.getElementById('userArea').style.display = "block";
        }

    }
 ending();
})


AreaZone.addEventListener('change', e => {

    e.preventDefault();
 waiting();
    $('#Detail').empty();
    $('#id_area').empty();
    var myTag = AreaZone.value;

    let url = '/api/get-area-info/'
    $.ajax({
        type: 'GET',
        data: {
            'myTag': myTag,
        },

        dataType: "json",
        url: url,
    }).done(function (data) {
        for (obj in data.mylist) {
            const mlist = data.mylist[obj]
            var content = '';
            content += '<option value=' + mlist.id + '>' + mlist.name + '</option>';

            $('#Detail').append(content);
            $('#id_area').append(content);
                ending();
        }
    })
           .fail(function (xhr, status, error) {
            ending(1,error);
        });
});

userSave.addEventListener('click', e => {
    e.preventDefault();
 waiting();

    id_codemeli = document.getElementById('id_codemeli').value
    Password1 = document.getElementById('Password1').value
    id_name = document.getElementById('id_name').value
    id_lname = document.getElementById('id_lname').value
    id_mobail = document.getElementById('id_mobail').value
    userZone = document.getElementById('Master').value
    userStorage = document.getElementById('Storage').value
    userArea = document.getElementById('Detail').value
    semat = document.getElementById('semat').value
    if (semat === "0"){
        alarm('error','لطفا سمت را انتخاب کنید')
        ending()
        return false
    }

    if (id_codemeli.length === 0){
        alarm('error','لطفا کد ملی را وارد کنید')
        ending()
        return false
    }
       if (id_name.length === 0){
        alarm('error','لطفا نام را وارد کنید')
        ending()
        return false
    }
              if (id_lname.length === 0){
        alarm('error','لطفا نام خانوادگی را وارد کنید')
        ending()
        return false
    }
                     if (id_mobail.length !== 11){
        alarm('error','لطفا شماره همراه را وارد کنید')
        ending()
        return false
    }


    let url = '/UserSave/'
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id_name': id_name,
            'id_codemeli': id_codemeli,
            'Password1': Password1,
            'id_lname': id_lname,
            'id_mobail': id_mobail,
            'userZone': userZone,
            'userStorage': userStorage,
            'userArea': userArea,
            'Mylad': Mylad.value,
            'semat': semat,
        },
        dataType: "json",
        url: url,
    }).done(function (data) {
        if (data.message ==='success') {
            alarm('success', 'عملیات موفق ، کاربر به درستی ایجاد شد')
            window.location.href = window.location.href;
        }else{
            alarm('error',data.message)
        }
  ending();
    })
         .fail(function (xhr, status, error) {
            ending(1,error);
        });
});

function GetArea(){
waiting();
let selectElement = document.getElementById('id_zone')
let selectedValues = Array.from(selectElement.selectedOptions)
        .map(option => option.value)


 $.ajax({
        type: 'GET',
        data: {

            'myTag': selectedValues.toString(),
        },
        dataType: "json",
        url: '/api/get-area-info/',
    }).done(function (data) {

        $('#id_area').empty()
        for (obj in data.mylist) {

            const mlist = data.mylist[obj]
            var content = '';

              content += '<option value=' + mlist.id + '>' + mlist.name  +' ('+ mlist.zone + ')</option>';

            $('#id_area').append(content);

        }
         ending();
    })
        .fail(function (xhr, status, error) {
            ending(1,error);
        });

}






function RemoveRow() {
    var $this = $(this);
 waiting();
     var table = document.getElementById('mytab2')
    userid = document.getElementById('userId').value
    var idsArr2 = [];
    $('.checkbox1:checked').each(function () {
        idsArr2.push($(this).attr('data-id'));
    });
    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید')
    } else {

        var strIds2 = idsArr2.join(",");
    }

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'strIds': strIds2,
            'userid': userid,
        },
        url: /RemoveGSUSER/,
        dataType: "json",
        }).done(function (resp) {
            obj = 0
            if (resp.message === "success") {
                $('.checkbox1:checked').each(function () {

                    $(this).parents("tr").remove();
                    var content = '';
                    const mlist = resp.mylist[obj]
                    content += ' <tr><td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + mlist.id + '">'
                    content += ' <td>' + mlist.gsid + '</td>'
                    content += '<td>' + mlist.name + '</td>'
                    content += '<td>' + mlist.area + '</td>'
                    content += '</td>'
                    content += '</tr>'
                    $('#myTable tbody').append(content)
                    obj += 1
                });
                alarm('success', 'عملیات بدرستی انجام شد')
                $('.check_alldell').prop('checked', false);
                document.getElementById('countgs').innerText="("+table.tBodies[0].rows.length + "مورد)"
                 ending();
            } else {
                alarm('danger', 'عملیات شکست خورد')
  ending();
            }
    })
            .fail(function (xhr, status, error) {
            ending(1,error);
        });
    return false;
};

function AddRow() {
    var $this = $(this);

    var table = document.getElementById('mytab2')
    userid = document.getElementById('userId').value
    var idsArr2 = [];
    $('.checkbox:checked').each(function () {
        idsArr2.push($(this).attr('data-id'));
    });
    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید')
    } else {

        var strIds2 = idsArr2.join(",");
    }

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'strIds': strIds2,
            'userid': userid,
        },
        url: /AddGSUSER/,
        dataType: "json",
    }).done(function (resp) {

            obj = 0
            if (resp.message === "success") {
                $('.checkbox:checked').each(function () {

                    $(this).parents("tr").remove();
                    var content = '';

                    const mlist = resp.mylist[obj]
                    content += ' <tr><td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox1" data-id="' + mlist.id + '">'
                    content += ' <td>' + mlist.gsid + '</td>'
                    content += '<td>' + mlist.name + '</td>'
                    content += '<td>' + mlist.area + '</td>'
                    content += '</td>'
                    content += '</tr>'
                    obj += 1
                    $('#mytab2 tbody').append(content)


                });
                alarm('success', 'عملیات بدرستی انجام شد')
                $('.check_all').prop('checked', false);
                document.getElementById('countgs').innerText="("+table.tBodies[0].rows.length + "مورد)"
            ending();
            } else {
                alarm('danger', 'عملیات شکست خورد')
 ending();
            }
    })
        .fail(function (xhr, status, error) {
            ending(1,error);
        });
    return false;
};
function GetRoles(id) {
  waiting();
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': id,
        },
        url:'/accounts/GetRole/',
        dataType: "json",
        }).done(function (resp) {
            if (resp.message === 'success'){
                 var content = '';
                 $('#tblrole tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    content += '<tr id="tr"'+mlist.id+'>'
                    content +='<td>'+mlist.permission +'</td>'
                    content +='<td> <select name="selectRole" id="selectRole">'

                    if (mlist.aid === 'view'){
                        content +='<option id="1" selected value="view">مشاهده</option>'
                    }else{
                        content +='<option id="1" value="view">مشاهده</option>'
                    }
                    if (mlist.aid === 'create'){
                        content +='<option id="2"  selected value="create">مشاهده و ایجاد</option>'
                    }else{
                        content +='<option id="2"  value="create">مشاهده و ایجاد</option>'
                    }
                    if (mlist.aid === 'full'){
                        content +='<option  id="3" selected value="full">دسترسی کامل</option>'
                    }else{
                        content +='<option id="3"  value="full">دسترسی کامل</option>'
                    }
                    if (mlist.aid === 'no'){
                        content +='<option  id="4" selected value="no">عدم دسترسی</option>'
                    }else{
                        content +='<option  id="4"  value="no">عدم دسترسی</option>'
                    }


                    content +='</select></td>'
                    content +='</td></td>'

                }
                $('#tblrole tbody').append(content)

            }else{
                alert('no')
            }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1,error);
        });
}




