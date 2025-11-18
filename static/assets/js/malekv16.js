const inputCard = document.getElementById('SaveUserId')
const EditUser = document.getElementById('editUser')
const EditBtn = document.getElementById('SaveEditUserId')
const AreaZone = document.getElementById('Master')


const inputState = document.getElementById('inputState')
const Mylad = document.getElementById('Mylad')
const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

function getMalek(val) {
waiting()
  
    document.getElementById('IdGs').value = val;
    var tableHeaderRowCount = 1;
    var table = document.getElementById('tblList');
    var rowCount = table.rows.length;
    for (var i = tableHeaderRowCount; i < rowCount; i++) {
        table.deleteRow(tableHeaderRowCount);
    }
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': val,
        },
        dataType: "json",
        url: '/showmalek/',
    }).done(function (data) {
        if (data.ok === 1) {
            $('#exampleModal1').modal('show');
            for (obj in data.mylist) {
                const mlist = data.mylist[obj]

                var content = '';
                content += '<tr id="' + 1 + '">';
                content += '<td id="fname">' + mlist.name + '</td>';
                content += '<td id="lname">' + mlist.lname + '</td>';
                content += '<td id="cmeli">' + mlist.codemeli + '</td>';
                content += '<td id="tell">' + mlist.mobail + '</td>';


                $('#tblList tbody').append(content);
               ending();
            }
        } else {
            alarm('warning', 'هنوز به این جایگاه مالکی معرفی نکردید ، ابتدا از قسمت کاربران یک کاربر جدید ایجاد کنید و از لیست جایگاه های کاربر ، این جایگاه را اضافه کنید')
           ending();
        }
    });
}

function GetArea() {

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
            content += '<option value=' + mlist.id + '>' + mlist.name + ' (' + mlist.zone + ')</option>';

            $('#id_area').append(content);

        }
    })

}

inputCard.addEventListener('click', e => {

    e.preventDefault();
    var $this = $(this);
waiting()
  
    let url = '/SaveUsr/'
    let CodMeli = document.getElementById('CodMeli').value
    let PassId = document.getElementById('PassId').value
    let IdGs = document.getElementById('IdGs').value
    let firstNameId = document.getElementById('firstNameId').value
    let lastNameId = document.getElementById('lastNameId').value
    let mobailId = document.getElementById('mobailId').value


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'CodMeli': CodMeli,
            'PassId': PassId,
            'IdGs': IdGs,
            'firstNameId': firstNameId,
            'lastNameId': lastNameId,
            'mobailId': mobailId,
        },
        url: url,
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {
                getMalek(IdGs)
                alarm('success', 'عملیات موفق ، ')
               ending();
            } else {
                getMalek(IdGs)
                $('#exampleModal1').modal('show');

            }
        }
    });
    return false;
});


EditUser.addEventListener('click', e => {

    e.preventDefault();
    var $this = $(this);
waiting()
  
    document.getElementById('CodMeli1').value = document.getElementById('cmeli').innerText

    document.getElementById('firstNameId1').value = document.getElementById('fname').innerText
    document.getElementById('lastNameId1').value = document.getElementById('lname').innerText
    document.getElementById('mobailId1').value = document.getElementById('tell').innerText
});

EditBtn.addEventListener('click', e => {

    e.preventDefault();
    var $this = $(this);
waiting()
  
    let url = '/SaveEditUsr/'
    let CodMeli = document.getElementById('CodMeli1').value
    let oldCodeMeli = document.getElementById('cmeli').innerText
    let IdGs = document.getElementById('IdGs').value
    let firstNameId = document.getElementById('firstNameId1').value
    let lastNameId = document.getElementById('lastNameId1').value
    let mobailId = document.getElementById('mobailId1').value


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'CodMeli': CodMeli,
            'oldCodeMeli': oldCodeMeli,
            'IdGs': IdGs,
            'firstNameId': firstNameId,
            'lastNameId': lastNameId,
            'mobailId': mobailId,
        },
        url: url,
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {
               ending();
                getMalek(IdGs)
            } else {
                getMalek(IdGs)

            }
        }
    });
    return false;
});


function getArea() {
waiting()
  
    var myTag = document.getElementById('Master').value

    $('#id_area2').empty();

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

            $('#id_area2').append(content);

           ending();
        }
    })
}


function SaveAddGs() {
waiting()
  

    let url = '/SaveAddGs/'
    let gsidGs = document.getElementById('gsidgs').value
    let nameGs = document.getElementById('namegs').value
    let addressGs = document.getElementById('addressgs').value
    let tellGs = document.getElementById('tellgs').value
    let master = document.getElementById('Master').value
    let id_area = document.getElementById('id_area2').value


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'gsidGs': gsidGs,
            'nameGs': nameGs,
            'addressGs': addressGs,
            'tellGs': tellGs,
            'master': master,
            'id_area': id_area,
        },
        url: url,
        dataType: "json",
    }).done(function (data) {
        const mlist = data.mylist[0]
        var content = '';

        content += '<td>' + mlist.gsid + '</td>';
        content += '<td>' + mlist.name + '</td>';
        content += '<td>' + mlist.zone + '</td>';
        content += '<td>' + mlist.area + '</td>';
        content += '<td>' + mlist.address + '</td>';
        content += '<td>' + mlist.tell + '</td>';
        content += ' <td style="width: 45%">'
        content += '<a style="color: #f6f7ff" href="#" class="btn nav-link bg-info-bright" title="مشخصات مالک" onclick="getMalek(' + mlist.id + ')" data-toggle="modal"><i data-feather="list" aria-hidden="true"></i>مالک </a>'
        content += '<a style="color: #f6f7ff" href="#" class="btn nav-link bg-secondary-bright" title="لیست نازل ها"\n' +
            '                       onclick="getMalek(' + mlist.id + ')" data-toggle="modal" data-target="#exampleModal1">\n' +
            '                        نازلها\n' +
            '                    </a>'
        content += ' <a style="color: #f6f7ff" href="#" class="btn nav-link bg-warning-bright" title="ویرایش"\n' +
            '                       onclick="getMalek(' + mlist.id + ')" data-toggle="modal" data-target="#exampleModal1">\n' +
            '                        <i data-feather="edit" aria-hidden="true"></i>\n' +
            '                    </a>'
        content += '</td>'
        $('#myTable tbody').append(content);
    })
    alarm('success', 'عملیات موفق ، جایگاه به درستی ایجاد شد')
   ending();
};


function getNazel(val) {
    document.getElementById('IdGs').value = val;
    document.getElementById('editidNazel').value = val;
waiting()
  
    var tableHeaderRowCount = 1;
    var table = document.getElementById('tblListNazel');
    var rowCount = table.rows.length;
    for (var i = tableHeaderRowCount; i < rowCount; i++) {
        table.deleteRow(tableHeaderRowCount);
    }

    var url = '/getNazel/'

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': val,

        },
        dataType: "json",
        url: url,
    }).done(function (data) {

        if (data.ok === 1) {

            for (obj in data.mylist) {
                const mlist = data.mylist[obj]

                var content = '';
                content += '<tr id="idn">' + mlist.id + '</td>';
                content += '<td id="number">' + mlist.number + '</td>';
                content += '<td id="product">' + mlist.product + '</td>';
                content += '<td id="master">' + mlist.master + '</td>';
                content += '<td id="pinpad">' + mlist.pinpad + '</td>';
                content += '<td id="pumpbrand">' + mlist.pumpbrand + '</td>';
                content += '<td id="active">' + mlist.actived + '</td>';


                $('#tblListNazel tbody').append(content);
               ending();
            }
        } else {
            alarm('warning', 'هیچ نازلی برای این جایگاه تعریف نشده')
           ending();
        }
    });
}



function SaveNazelAdd() {
waiting()
  
    let url = '/SaveNazel/'
    let nazelnuid = document.getElementById('nazelnuid').value
    let productid = document.getElementById('productid').value
    let masterid = document.getElementById('masterid').value
    let pinpadid = document.getElementById('pinpadid').value
    let nazelmodelid = document.getElementById('nazelmodelid').value
    let activeid = document.getElementById('activeid').value
    let id = document.getElementById('IdGs').value

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'nazelnuid': nazelnuid,
            'productid': productid,
            'masterid': masterid,
            'pinpadid': pinpadid,
            'nazelmodelid': nazelmodelid,
            'activeid': activeid,
            'id': id,
        },
        url: url,
        dataType: "json",
    }).done(function (data) {
        if (data.ok === 1) {
            const mlist = data.mylist[0]
            var content = '';
            content += '<tr id="idn">' + mlist.id + '</td>';
            content += '<td id="number">' + mlist.number + '</td>';
            content += '<td id="product">' + mlist.product + '</td>';
            content += '<td id="master">' + mlist.master + '</td>';
            content += '<td id="pinpad">' + mlist.pinpad + '</td>';
            content += '<td id="pumpbrand">' + mlist.pumpbrand + '</td>';
            content += '<td id="active">' + mlist.active + '</td>';


            $('#tblListNazel tbody').append(content);
            alarm('success', 'عملیات موفق ، نازل به درستی ایجاد شد')
           ending();
        } else {
            alarm('warning', 'عملیات ناموفق ، نازل تکراری است')
            ending();
        }
    })
     .fail(function (xhr, status, error) {
         ending(1,error);
     })
};

function editItem(val, id,rnd) {
    document.getElementById('parametr_id').value = val
waiting();
    $.ajax({
        cache: false,
        url: "/api/get-gs-edit",
        data: {
            val: val,
            rnd: rnd,
            id: id,
        },
      }).done(function (data) {
          if (data.message ==='success'){

            if (val < 51 || val > 90) {

                $('#item_info').empty();

                for (obj in data.list) {

                    const mlist = data.list[obj]
                    var content = '';
                    if (data.parametr === mlist.id) {
                        content += '<option selected value=' + mlist.id + '>' + mlist.name + '</option>';
                    } else {
                        content += '<option value=' + mlist.id + '>' + mlist.name + '</option>';
                    }
                    $('#item_info').append(content);

                }
            } else {
                document.getElementById('item_info2').value = data.parametr
            }
            }else{
              alarm('error',data.message)
          }
     ending();
        })
       .fail(function (xhr, status, error) {
      ending();
        });
}

function updateItem(id,rnd) {
    var val = document.getElementById('parametr_id').value
    if (val < 51 || val> 90) {
        var newval = document.getElementById('item_info').value
    } else {
        var newval = document.getElementById('item_info2').value
    }
waiting()

    $.ajax({
        cache: false,
        url: "/api/set-gs-edit",
        data: {
            val: val,
            id: id,
            rnd: rnd,
            newval: newval,
        },
        success: function (data) {
 if (data.message ==='success'){
            if (data.val === 1) {
                document.getElementById('operator_Id').innerText = data.newname
            }
            if (data.val === 2) {
                document.getElementById('ipc_Id').innerText = data.newname
            }
            if (data.val === 3) {
                document.getElementById('rack_Id').innerText = data.newname
            }
            if (data.val === 4) {
                document.getElementById('modem_Id').innerText = data.newname
            }
            if (data.val === 5) {
                document.getElementById('Status_Id').innerText = data.newname
            }
            if (data.val === 6) {
                if (data.newname === '0') {
                    vl = 'آفلاین'
                } else {
                    vl = 'آنلاین'
                }
                document.getElementById('Online_Id').innerText = vl
            }
            if (data.val === 7) {
                if (data.newname === '0') {
                    vl = 'خیر'
                } else {
                    vl = 'بلی'
                }
                document.getElementById('Montakhab_Id').innerText = vl
            }
            if (data.val === 8) {
                if (data.newname === '0') {
                    vl = 'موجود نیست'
                    document.getElementById('Bazdid_ok').classList.remove('text-success');
                    document.getElementById('Bazdid_ok').classList.add('text-danger');
                    document.getElementById('Bazdid_ok').classList.remove('fa-check');
                    document.getElementById('Bazdid_ok').classList.add('fa-times');
                } else {
                    vl = 'انجام شد'
                    document.getElementById('Bazdid_ok').classList.add('text-success');
                    document.getElementById('Bazdid_ok').classList.remove('text-danger');
                    document.getElementById('Bazdid_ok').classList.add('fa-check');
                    document.getElementById('Bazdid_ok').classList.remove('fa-times');
                }
                document.getElementById('Bazdid_Id').innerText = vl
            }
            if (data.val === 9) {
                if (data.newname === '0') {
                    vl = 'موجود نیست'
                    document.getElementById('final_ok').classList.remove('text-success');
                    document.getElementById('final_ok').classList.add('text-danger');
                    document.getElementById('final_ok').classList.remove('fa-check');
                    document.getElementById('final_ok').classList.add('fa-times');
                } else {
                    vl = 'انجام شد'
                    document.getElementById('final_ok').classList.add('text-success');
                    document.getElementById('final_ok').classList.remove('text-danger');
                    document.getElementById('final_ok').classList.add('fa-check');
                    document.getElementById('final_ok').classList.remove('fa-times');
                }
                document.getElementById('Final_Id').innerText = vl
            }
            if (data.val === 10) {
                if (data.newname === '0') {
                    vl = 'خیر'
                } else {
                    vl = 'بلی'
                }
                document.getElementById('Qrcode_Id').innerText = vl
            }
            if (data.val === 11) {
                if (data.newname === '0') {
                    vl = 'ندارد'
                } else {
                    vl = 'دارد'
                }
                document.getElementById('isbank_Id').innerText = vl
            }
            if (data.val === 12) {
                if (data.newname === '0') {
                    vl = 'ندارد'
                } else {
                    vl = 'دارد'
                }
                document.getElementById('ispaystation_Id').innerText = vl
            }
            if (data.val === 16) {
                if (data.newname === '0') {
                    vl = 'ندارد'
                } else {
                    vl = 'دارد'
                }
                document.getElementById('isbankmeli_Id').innerText = vl
            }
            if (data.val === 13) {
                document.getElementById('GsStatus_Id').innerText = data.newname
            }
            if (data.val === 14) {
                if (data.newname === '0') {
                    vl = 'ندارد'
                } else {
                    vl = 'دارد'
                }
                document.getElementById('isticket_Id').innerText = vl
            }
            if (data.val === 15) {
                if (data.newname === '0') {

                    vl = 'ضعیف';
                } else {
                    vl = 'مطلوب';
                }
                document.getElementById('GpsSignal_Id').innerText = vl;
            }
            if (data.val === 17) {
                document.getElementById('city_Id').innerText = data.newname
            }
            if (data.val === 51) {
                document.getElementById('simcart_Id').innerText = data.newname
            }
            if (data.val === 52) {
                document.getElementById('PostalCode_Id').innerText = data.newname
            }
            if (data.val === 53) {
                document.getElementById('Tell_Id').innerText = data.newname
            }
            if (data.val === 54) {
                document.getElementById('Requarment_Id').innerText = data.newname

                if (data.newname) {
                    document.getElementById('Requarment_ok').classList.add('text-success');
                    document.getElementById('Requarment_ok').classList.remove('text-danger');
                    document.getElementById('Requarment_ok').classList.add('fa-check');
                    document.getElementById('Requarment_ok').classList.remove('fa-times');

                } else {
                    document.getElementById('Requarment_ok').classList.remove('text-success');
                    document.getElementById('Requarment_ok').classList.add('text-danger');
                    document.getElementById('Requarment_ok').classList.remove('fa-check');
                    document.getElementById('Requarment_ok').classList.add('fa-times');

                }
            }
            if (data.val === 55) {
                document.getElementById('Sam_Id').innerText = data.newname

                if (data.newname) {
                    document.getElementById('Samt_ok').classList.add('text-success');
                    document.getElementById('Samt_ok').classList.remove('text-danger');
                    document.getElementById('Samt_ok').classList.add('fa-check');
                    document.getElementById('Samt_ok').classList.remove('fa-times');

                } else {
                    document.getElementById('Samt_ok').classList.remove('text-success');
                    document.getElementById('Samt_ok').classList.add('text-danger');
                    document.getElementById('Samt_ok').classList.remove('fa-check');
                    document.getElementById('Samt_ok').classList.add('fa-times');

                }
            }
            if (data.val === 56) {
                document.getElementById('Bank_Id').innerText = data.newname

                if (data.newname) {
                    document.getElementById('Bank_ok').classList.add('text-success');
                    document.getElementById('Bank_ok').classList.remove('text-danger');
                    document.getElementById('Bank_ok').classList.add('fa-check');
                    document.getElementById('Bank_ok').classList.remove('fa-times');

                } else {
                    document.getElementById('Bank_ok').classList.remove('text-success');
                    document.getElementById('Bank_ok').classList.add('text-danger');
                    document.getElementById('Bank_ok').classList.remove('fa-check');
                    document.getElementById('Bank_ok').classList.add('fa-times');

                }
            }
            if (data.val === 57) {
                document.getElementById('Start_Id').innerText = data.newname

                if (data.newname) {
                    document.getElementById('Start_ok').classList.add('text-success');
                    document.getElementById('Start_ok').classList.remove('text-danger');
                    document.getElementById('Start_ok').classList.add('fa-check');
                    document.getElementById('Start_ok').classList.remove('fa-times');

                } else {
                    document.getElementById('Start_ok').classList.remove('text-success');
                    document.getElementById('Start_ok').classList.add('text-danger');
                    document.getElementById('Start_ok').classList.remove('fa-check');
                    document.getElementById('Start_ok').classList.add('fa-times');

                }
            }
            if (data.val === 58) {
                document.getElementById('Name_Id').innerText = data.newname
            }
            if (data.val === 59) {
                document.getElementById('Address_Id').innerText = data.newname
            }
            if (data.val === 60) {
                document.getElementById('Gps_Id').innerText = data.newname
            }
            if (data.val === 61) {
                    document.getElementById('m_benzin_Id').innerText = data.newname;
                }
            if (data.val === 62) {
                    document.getElementById('m_super_Id').innerText = data.newname;
                }
            if (data.val === 63) {
                    document.getElementById('m_naftgaz_Id').innerText = data.newname;
                }
            if (data.val === 64) {
                document.getElementById('Mohandesi_Id').innerText = data.newname
                        if(data.newname=="0"){
                            document.getElementById('Mohandesi_Id').innerText ='بدون محدودیت'
                        }
            }

            if (data.val === 95) {
                document.getElementById('printer_Id').innerText = data.newname
            }
              if (data.val === 96) {
                document.getElementById('thinclient_Id').innerText = data.newname
            }
            alarm('success', 'اطلاعات جایگاه بروزرسانی شد')
     }else{
              alarm('error',data.message)
          }
           ending();
        },
        error: function (xhr, status, error) {
           ending();



        }
    });
}




function geteditPump(val) {
    document.getElementById('nazel_id').value = val
waiting()
    $.ajax({
        cache: false,
        url: "/api/get-edit-pump",
        data: {
            val: val,

        },
        success: function (data) {


                $('#item_pump_status').empty();
                for (obj in data.liststatuspump) {
                    const mlist = data.liststatuspump[obj]
                    var content = '';
                    if (data.statuspan === mlist.id) {
                        content += '<option selected value=' + mlist.id + '>' + mlist.name + '</option>';
                    } else {
                        content += '<option value=' + mlist.id + '>' + mlist.name + '</option>';
                    }
                    $('#item_pump_status').append(content);

                }

                $('#item_status_pump').empty();
                for (obj in data.liststatusmodel) {
                    const mlist = data.liststatusmodel[obj]
                    var content = '';
                    if (data.pumpbrand === mlist.id) {
                        content += '<option selected value=' + mlist.id + '>' + mlist.name + '</option>';
                    } else {
                        content += '<option value=' + mlist.id + '>' + mlist.name + '</option>';
                    }
                    $('#item_status_pump').append(content);
                }

                $('#item_product_pump').empty();
                for (obj in data.listproduct) {
                    const mlist = data.listproduct[obj]
                    var content = '';
                    if (data.product === mlist.id) {
                        content += '<option selected value=' + mlist.id + '>' + mlist.name + '</option>';
                    } else {
                        content += '<option value=' + mlist.id + '>' + mlist.name + '</option>';
                    }
                    $('#item_product_pump').append(content);
                }

                document.getElementById('sakoo_number').value = data.sakoo
                document.getElementById('tolombe_number').value = data.tolombe
                document.getElementById('nazel_number').value = data.nazel
                document.getElementById('nazelcountshomarande').value = data.nazelcountshomarande
ending();

        },
        error: function (xhr, status, error) {
ending();


        }
    });
}

function seteditPump() {
    var val = document.getElementById('nazel_id').value
    var item_pump_status = document.getElementById('item_pump_status').value
    var item_status_pump = document.getElementById('item_status_pump').value
    var item_product_pump = document.getElementById('item_product_pump').value
    var sakoo_number = document.getElementById('sakoo_number').value
    var tolombe_number = document.getElementById('tolombe_number').value
    var nazel_number = document.getElementById('nazel_number').value
    var nazelcountshomarande = document.getElementById('nazelcountshomarande').value
    if (nazel_number.length < 1){
        alarm('error','شماره نازل را وارد کنید')
        return false
    }
        if (tolombe_number.length < 1){
        alarm('error','شماره تلمبه را وارد کنید')
        return false
    }
            if (sakoo_number.length < 1){
        alarm('error','شماره سکو را وارد کنید')
        return false
    }
waiting()

    $.ajax({
        cache: false,
        url: "/api/set-edit-pump",
        data: {
            val: val,
            item_pump_status: item_pump_status,
            item_status_pump: item_status_pump,
            item_product_pump: item_product_pump,
            sakoo_number: sakoo_number,
            tolombe_number: tolombe_number,
            nazel_number: nazel_number,
            nazelcountshomarande: nazelcountshomarande,
        },

        success: function (data) {
            if (data.message === 'success'){
                document.getElementById('status'+val).innerText = data.item_pump_status_name
                document.getElementById('id_brand'+val).innerText = data.item_status_pump_name
                // document.getElementById('item_product_pump').value = item_product_pump_name
                document.getElementById('id_sakoo'+val).innerText = sakoo_number
                document.getElementById('id_tolombe'+val).innerText = tolombe_number
                document.getElementById('id_nazel'+val).innerText = nazel_number


                alarm('success','اطلاعات به درستی ویرایش شد')
            }

           ending();
        },
        error: function (xhr, status, error) {
           ending();
        }
    });
}

function Download(item,val) {

     waiting();
    let url = '/api/showimgtek/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': item,
            'val': val,
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


function showlock(val,st) {
waiting()

    let url = '/api/ShowLock/'


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,
            'st': st,
        },
        url: url,
        dataType: "json",
    }).done(function (data) {
        $('#plomptbl tbody').empty()


             for (obj in data.polomps) {
                  var content = '';
                 const mlist = data.polomps[obj]

                 content += '<tr><td>'
                 content += mlist.serial
                 content += '</td></tr>'

                 $('#plomptbl tbody').append(content);
             }
                 ending();

    })
     .fail(function (xhr, status, error) {
         ending(1,error);
     })
};