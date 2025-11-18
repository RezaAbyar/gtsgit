const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;

function getStore(id) {
    waiting()

    document.getElementById('StoreId').value = id;
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': id,
        },
        url: '/pay/getStore/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === 'success') {
                var content = '';
                var i = 1
                $('#myTable tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    content += '<tr id="tr"' + mlist.id + '>'
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + mlist.id + '">'
                    content += '<td>' + parseInt(i) + '</td>'
                    content += '<td>' + mlist.serial + '</td></td>'
                    if (mlist.level === 0) {
                        content += '<td><img src="/static/assets/img/risk/work-started-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته خرابی نداشته" alt=""/> </td></td></tr>'
                    }
                    if (mlist.level === 1) {
                        content += '<td><img src="/static/assets/img/risk/low-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته یکبار معیوب شد" alt=""/> </td></td></tr>'
                    }
                    if (mlist.level === 2) {
                        content += '<td><img src="/static/assets/img/risk/medium-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته دو بار معیوب شد" alt=""/> </td></td></tr>'
                    }
                    if (mlist.level === 3) {
                        content += '<td><img src="/static/assets/img/risk/high-risk-alert-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته بیش از دو بار معیوب شد" alt=""/> </td></td></tr>'
                    }

                    i += 1
                }
                $('#myTable tbody').append(content)
                getStoretoTek(document.getElementById('id_tek').value)
                ending();
            } else {
                alert('no')
                ending();
            }
        }
    })
}

function getStoreTek(id) {
    waiting()

    StoreId = document.getElementById('StoreId').value
    var table = document.getElementById('mytab2')
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': id,
            'StoreId': StoreId,
        },
        url: '/pay/getStoreTek/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === 'success') {
                var content = '';
                var i = 1
                $('#mytab2 tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    content += '<tr id="tr"' + mlist.id + '>'
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox1" data-id="' + mlist.id + '">'
                    content += '<td>' + parseInt(i) + '</td>'
                    content += '<td>' + mlist.serial + '</td></td></tr>'
                    i += 1
                }
                $('#mytab2 tbody').append(content)
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)"
                ending();
            } else {
                alert('no')
                ending();
            }
        }
    })
}

function getStoretoTek(id) {
    waiting()

    StoreId = document.getElementById('StoreId').value
    var table = document.getElementById('mytab2')
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': id,
            'StoreId': StoreId,
        },
        url: '/pay/getStoretoTek/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === 'success') {
                var content = '';
                var i = 1
                $('#mytab2 tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    content += '<tr id="tr"' + mlist.id + '>'
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox1" data-id="' + mlist.id + '">'
                    content += '<td>' + parseInt(i) + '</td>'
                    content += '<td>' + mlist.serial + '</td></td>'
                    if (mlist.level === 0) {
                        content += '<td><img src="/static/assets/img/risk/work-started-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته خرابی نداشته" alt=""/> </td></td></tr>'
                    }
                    if (mlist.level === 1) {
                        content += '<td><img src="/static/assets/img/risk/low-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته یکبار معیوب شد" alt=""/> </td></td></tr>'
                    }
                    if (mlist.level === 2) {
                        content += '<td><img src="/static/assets/img/risk/medium-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته دو بار معیوب شد" alt=""/> </td></td></tr>'
                    }
                    if (mlist.level === 3) {
                        content += '<td><img src="/static/assets/img/risk/high-risk-alert-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته بیش از دو بار معیوب شد" alt=""/> </td></td></tr>'
                    }
                    i += 1
                }
                $('#mytab2 tbody').append(content)
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)"
                ending();
            } else {
                alert('no')
            }
        }
    })
}


function AddRow(val) {

    waiting()

    var $this = $(this);
    var table = document.getElementById('mytab2')

    userid = document.getElementById('id_tek').value

    if (userid === '-1') {
        alarm('warning', 'لطفا ابتدا یک تکنسین را انتخاب کنید')

        ending()
        return false
    }
    var idsArr2 = [];
    $('.checkbox:checked').each(function () {
        idsArr2.push($(this).attr('data-id'));
    });

    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید')
        ending()
        return false
    } else {

        var strIds2 = idsArr2.join(",");

    }

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'strIds': strIds2,
            'id_tek': userid,
            'val': val,
        },
        url: '/pay/AddSTORETEK/',
        dataType: "json",
        success: function (resp) {


            obj = 0
            if (resp.message === 'success') {
                $('.checkbox:checked').each(function () {

                    $(this).parents("tr").remove();

                    var content = '';
                    const mlist = resp.list[obj]
                    content += '<tr id="tr"' + mlist.id + '>'
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox1" data-id="' + mlist.id + '">'
                    content += '<td>جدید</td>'
                    content += '<td style="font-size: 20px;">' + mlist.serial + '</td></td>'
                    if (val === 1) {
                        content += '</tr>'
                    }
                    if (val === 2) {
                        content += '<td>' + mlist.st + '</td></td></tr>'

                    }
                    obj += 1
                    $('#mytab2 tbody').append(content)

                });
                ending()
                alarm('success', 'عملیات بدرستی انجام شد')
                $('.check_all').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)"

            } else {
                ending()
                alarm('danger', 'عملیات شکست خورد')
            }
        },
        error: function (xhr, status, error) {
            ending(1,error);
        }
    });
    return false;
};

function AddGS() {
    waiting()

    var $this = $(this);
    var table = document.getElementById('mytab2')
    userid = document.getElementById('id_tek').value

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
            'id_tek': userid,
        },
        url: '/pay/AddSTOREGS/',
        dataType: "json",
        success: function (resp) {
            obj = 0
            if (resp.message === 'success') {
                $('.checkbox:checked').each(function () {

                    $(this).parents("tr").remove();


                });
                alarm('success', 'عملیات بدرستی انجام شد')
                $('.check_all').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)"
                ending();
            } else {
                alarm('danger', 'عملیات شکست خورد')
                ending();

            }

        }
    });
    return false;
};

function RemoveRow(val) {
    waiting()
    ;

    var $this = $(this);
    var tablep = document.getElementById('tblpost')
    var table = document.getElementById('mytab2')
    userid = document.getElementById('id_tek').value
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
            'val': val,
        },
        url: '/pay/RemoveSTORETEK/',
        dataType: "json",
        success: function (resp) {
            obj = 0
            if (resp.message === "success") {
                $('.checkbox1:checked').each(function () {
                    $(this).parents("tr").remove();
                    if (resp.val !== '3') {
                        var content = '';
                        const mlist = resp.list[obj]
                        content += '<tr id="tr"' + mlist.id + '>'
                        content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + mlist.id + '">'
                        content += '<td>برگشت خورده</td>'
                        content += '<td style="font-size: 20px;">' + mlist.serial + '</td></td>'
                        if (val === 1) {
                            content += '</tr>'
                        }
                        if (val === 2) {
                            content += '<td>' + mlist.st + '</td></td>'
                            content += '<td>' + mlist.user + '</td></td></tr>'
                        }

                        $('#myTable tbody').append(content)
                        obj += 1
                    } else {

                        var content = '';
                        const mlist = resp.list[obj]
                        content += '<tr id="tr"' + mlist.id + '>'
                        content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + mlist.id + '">'
                        content += '<td>جدید</td>'
                        content += '<td style="font-size: 20px;">' + mlist.serial + '</td></td>'
                        if (val === 1) {
                            content += '</tr>'
                        }
                        if (val === 2) {
                            content += '<td>' + mlist.st + '</td></td>'
                            content += '<td>' + mlist.user + '</td></td></tr>'
                        }

                        $('#tblpost tbody').append(content)
                        obj += 1
                    }
                });
                alarm('success', 'عملیات بدرستی انجام شد')
                 ending();
                $('.check_alldell').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)"
                document.getElementById('countpost').innerText = "(" + tablep.tBodies[0].rows.length + "مورد)"
                ending();
            } else {
                alarm('danger', 'عملیات شکست خورد')
                ending(1,error);

            }

        }
    });
    return false;
};

function sortTable() {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById("listTable");
    switching = true;
    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
        //start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /*Loop through all table rows (except the
        first, which contains table headers):*/
        for (i = 1; i < (rows.length - 1); i--) {
            //start by saying there should be no switching:
            shouldSwitch = false;
            /*Get the two elements you want to compare,
            one from current row and one from the next:*/
            x = rows[i].getElementsByTagName("TD")[0];
            y = rows[i + 1].getElementsByTagName("TD")[0];
            //check if the two rows should switch place:
            if (x.innerHTML.toUpperCase() > y.innerHTML.toUpperCase()) {
                //if so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            /*If a switch has been marked, make the switch
            and mark that a switch has been done:*/
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}

function sortTable2(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("myTable2");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "asc";
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

function CheckSerial(serial, id, st) {

    waiting()
    var rows = document.getElementById("listTable").rows;
    var $this = $(this);
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'serial': serial,
            'id': id,
            'st': st,
        },
        url: '/pay/checkserial/',
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "level2") {
            ending()
            alarm('error', resp.payam)
            return false
        }
        if (resp.message === "level3") {
            ending()
            alarm('error', resp.payam)
            return false
        }

        if (resp.message === "success") {
            document.getElementById('lblId').innerHTML = " تعداد " + resp.tedad
            var content = '';
            const mlist = resp.mylist[0]
            content += '<tr id="r' + mlist.id + '">'


            var table = document.getElementById("listTable");
            var row = table.insertRow(0);
            // var tr = table.insertRow();
            row.id = "r" + mlist.id

            var cell1 = row.insertCell(0);
            var cell2 = row.insertCell(1);
            var cell3 = row.insertCell(2);
            cell1.innerHTML = mlist.serial;
            if (id === 0) {
                cell2.innerHTML = "<a onclick=\"removehis2(" + mlist.id + ")\" class=\"btn btn-warning\"> حذف</a>"
            } else {
                cell2.innerHTML = "<a onclick=\"removehis(" + mlist.id + ")\" class=\"btn btn-warning\"> حذف</a>"
            }
            cell3.innerHTML = "<a style='color: white' onclick=\"addstore(" + mlist.id + ")\" data-target=\"#addstorefun\" data-toggle=\"modal\" class=\"btn btn-primary\">قطعات مصرفی</a>"


            ending()
        } else {
            ending()
            alarm('danger', 'مقدار باید بصورت عدد و بصورت انگلیسی باشد و تعداد کارکتر مجاز باید بین 10 تا 12 باشد')
        }

    })
        .fail(function (xhr, status, error) {
            ending(1,error);

        });
    return false;
};


function plusstore(val,val2){
    waiting()
    storeid = document.getElementById('store_id_fun').value
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,
            'val2': val2,
            'storeid': storeid,
        },
        url: '/pay/plusstore/',
        dataType: "json",
        success: function (resp) {
            document.getElementById('id_value-'+val).value = resp.newval

ending()
        },
         error: function (xhr, status, error) {
            ending(1,error);
         }

    })
}


function addstore(val) {
    waiting()
    document.getElementById('store_id_fun').value = val
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': val,
        },
        url: '/pay/addstorefunc/',
        dataType: "json",
        success: function (resp) {

            $('#id_repairstore').empty()
            var content = '';

            var i=0;
            for (obj in resp.storename) {
                const mlist = resp.storename[obj]
                i +=1
                // if (i===3 || i===6 || i===9 || i===12 ){
                //     content +='<div class="row">'
                // }


                 content +='<div class="row">'
                content +='<div class="col-2">'
                content += '<button onclick="plusstore('+mlist.id+',2)"  class="btn btn-danger">-</button>';
                content +='</div>'
                content +='<div class="col-3">'
                content += '<input readonly id="id_value-'+mlist.id+'" class="form-control text-primary text-center" value="'+mlist.tedad+'">';
                content +='</div><div class="col-6">'
                content += '<button onclick="plusstore('+mlist.id+',1)"  class="btn btn-success">'+mlist.name+'</button>';
                content +='</div>'
                content +='</div>'
                content +='</div>'



                    content +='<br>'


            }

            $('#id_repairstore').append(content);
            ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            $('#tableaddstore tbody').empty()
            var content = '';
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                content += '<tr id="r'+mlist.id+'">';
                content += '<td>' + mlist.name + '</td>';
                content += '<td>' + mlist.count + '</td>';
                content += '<td><a style="color: #f3fdf3" onclick="deletezone_repaire_store('+mlist.id+')" id="editUsernow" onclick="" class="btn nav-link bg-danger">حذف</a></td>'
                content += '</tr>';
            }
            $('#tableaddstore tbody').append(content);
            ending()
        },
         error: function (xhr, status, error) {
            ending(1,error);
         }

    })
}

function deletezone_repaire_store(val){
     waiting()

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': val,
        },
        url: '/pay/delete_store_item/',
        dataType: "json",
        success: function (resp) {
            document.getElementById('r' + val).remove()
alarm('info','قطعه مورد نظر بدرستی حذف شد')
            ending()
        },
         error: function (xhr, status, error) {
            ending(1,error);
         }
    })
}

function newstore() {
    store = document.getElementById('store_id_fun').value
    name = document.getElementById('id_repairstore').value
    amount = document.getElementById('id_amount').value
    waiting()
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'store': store,
            'name': name,
            'amount': amount,
        },
        url: '/pay/newstorefun/',
        dataType: "json",
        success: function (resp) {
            alarm('info','عملیات با موفقیت انجام شد.')
            addstore(store)
        },
         error: function (xhr, status, error) {
            ending(1,error);
         }
    })
}

function removehis(val) {
    var table = document.getElementById('listTable')
    var $this = $(this);
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': val,

        },
        url: '/pay/removeSerial/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {
                document.getElementById('r' + val).remove()
                alarm('info', 'با موفقیت حذف شد')

                document.getElementById('lblId').innerHTML = " تعداد " + resp.tedad

            }
        }
    });
    return false;
};


function removehis2(val) {
    var table = document.getElementById('listTable')
    var $this = $(this);
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': val,

        },
        url: '/pay/removeSerial2/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {
                document.getElementById('r' + val).remove()
                alarm('info', 'با موفقیت حذف شد')

                document.getElementById('lblId').innerHTML = " تعداد " + resp.tedad

            }
        }
    });
    return false;
};

function getsenddaghi(id) {
    waiting()

    document.getElementById('StoreId').value = id;
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': id,
        },
        url: '/pay/getsenddaghi/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === 'success') {
                var content = '';
                var i = 1
                $('#myTable tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    content += '<tr id="tr"' + mlist.id + '>'
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + mlist.id + '">'
                    content += '<td>' + parseInt(i) + '</td>'
                    content += '<td>' + mlist.serial + '</td></td></tr>'
                    i += 1
                }
                $('#myTable tbody').append(content)
                getStoretoTek(document.getElementById('id_tek').value)
                ending();
            } else {
                alert('no')
                ending();
            }
        }
    })
}

function AddRowlock(val) {

    waiting()

    var $this = $(this);
    var table = document.getElementById('mytab2')

    userid = document.getElementById('id_tek').value

    if (userid === '-1') {
        alarm('warning', 'لطفا ابتدا یک تکنسین را انتخاب کنید')

        ending()
        return false
    }
    var idsArr2 = [];
    $('.checkbox:checked').each(function () {
        idsArr2.push($(this).attr('data-id'));
    });

if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید')
        ending()
        return false
    } else {

        var strIds2 = idsArr2.join(",");

    }

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'strIds': strIds2,
            'id_tek': userid,
            'val': val,
        },
        url: '/lock/addlocktek/',
        dataType: "json",
        success: function (resp) {


            obj = 0
            if (resp.message === 'success') {
                $('.checkbox:checked').each(function () {

                    $(this).parents("tr").remove();

                    var content = '';
                    const mlist = resp.list[obj]
                    content += '<tr id="tr"' + mlist.id + '>'
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox1" data-id="' + mlist.id + '">'
                    content += '<td>جدید</td>'
                    content += '<td style="font-size: 20px;">' + mlist.serial + '</td></td>'
                    if (val === 1) {
                        content += '</tr>'
                    }
                    if (val === 2) {
                        content += '<td>' + mlist.st + '</td></td>'
                    }
                    content += '<td style="font-size: 20px;">' + mlist.user + '</td></td></tr>'
                    obj += 1
                    $('#mytab2 tbody').append(content)
                });
                ending()
                alarm('success', 'عملیات بدرستی انجام شد')
                $('.check_all').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)"

            } else {
                ending()
                alarm('danger', 'عملیات شکست خورد')
            }
        },
        error: function (xhr, status, error) {
            ending(1,error);
        }
    });
    return false;
};

function RemoveRowlock(val) {
    waiting()
    ;

    var $this = $(this);
    var tablep = document.getElementById('tblpost')
    var table = document.getElementById('mytab2')
    userid = document.getElementById('id_tek').value
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
            'val': val,
        },
        url: '/lock/removelocktek/',
        dataType: "json",
        success: function (resp) {
            obj = 0
            if (resp.message === "success") {
                $('.checkbox1:checked').each(function () {
                    $(this).parents("tr").remove();
                    if (resp.val !== '3') {
                        var content = '';
                        const mlist = resp.list[obj]
                        content += '<tr id="tr"' + mlist.id + '>'
                        content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + mlist.id + '">'
                        content += '<td>برگشت خورده</td>'
                        content += '<td style="font-size: 20px;">' + mlist.serial + '</td></td>'
                        if (val === 1) {
                            content += '</tr>'
                        }
                        if (val === 2) {
                            content += '<td>' + mlist.st + '</td></td>'
                            content += '<td>' + mlist.user + '</td></td></tr>'
                        }

                        $('#myTable tbody').append(content)
                        obj += 1
                    } else {

                        var content = '';
                        const mlist = resp.list[obj]
                        content += '<tr id="tr"' + mlist.id + '>'
                        content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + mlist.id + '">'
                        content += '<td>جدید</td>'
                        content += '<td style="font-size: 20px;">' + mlist.serial + '</td></td>'
                        if (val === 1) {
                            content += '</tr>'
                        }
                        if (val === 2) {
                            content += '<td>' + mlist.st + '</td></td>'
                            content += '<td>' + mlist.user + '</td></td></tr>'
                        }

                        $('#tblpost tbody').append(content)
                        obj += 1
                    }
                });
                alarm('success', 'عملیات بدرستی انجام شد')
                 ending();
                $('.check_alldell').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)"
                document.getElementById('countpost').innerText = "(" + tablep.tBodies[0].rows.length + "مورد)"
                ending();
            } else {
                alarm('danger', 'عملیات شکست خورد')
                ending(1,error);

            }

        }
    });
    return false;
};