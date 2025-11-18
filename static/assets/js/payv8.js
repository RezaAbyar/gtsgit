function ZaribSum() {

    var par = document.getElementById('parm1').value
    var mah = document.getElementById('mmozd').value

    document.getElementById('lparm1').value = FormatNumberBy3(Math.round((mah * par) / 100))
    document.getElementById('lparm1').value += " ریال"
}

function EzafeSum(id1, id2) {

    var par = document.getElementById('parm2').value
    var roz = document.getElementById('dmozd').value
    document.getElementById('lparm2').value = FormatNumberBy3(Math.round(roz / 7.33 * 1.4 * par));
    document.getElementById('lparm2').value += " ریال"
}

function getTekpay() {

    var priod = document.getElementById('id_period').value
    var tekid = document.getElementById('id_tek').value

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'priod': priod,
            'tekid': tekid,
        },
        url: '/pay/getTekpay/',
        dataType: "json",
        success: function (resp) {

            if (resp.message === "success") {


                $('#payTableList tbody').empty()
                for (obj in resp.paylist) {
                    const mlist = resp.paylist[obj]
                    var content = '';
                    content += '<tr id="' + mlist.id + '">';
                    content += '<td>' + mlist.name + '</td>'
                    content += ' <td class="text-center">' + mlist.count + '</td>'
                    if (mlist.id === 8 || mlist.id === 16) {
                        content += '<td style="color: #00a345"  class="text-center">' + mlist.price + '</td></tr>'
                    } else {
                        content += '<td class="text-center">' + mlist.price + '</td></tr>'
                    }

                    $('#payTableList tbody').append(content);

                }
                content = ""
                content += '<tr style="background: #7c1a03" id="trsum">';
                content += '<td>جمع</td>'
                content += ' <td class="text-center"></td>'
                content += '<td class="text-center">' + resp.paysum + '</td></tr>'
                $('#payTableList tbody').append(content);

                document.getElementById('tekname').innerText = "حقوق و دستمزد " + resp.tekname
                document.getElementById('parm1').value = resp.co
                document.getElementById('parm2').value = resp.pr
                ZaribSum()
                EzafeSum()

            }
        }
    })
}

function Period() {
    var priod = document.getElementById('id_period').value
    // document.getElementById('sarane').innerText = ""
    $('#listpayTable tbody').empty()
    $('#payTableList tbody').empty()
    // document.getElementById('parm1').value = ""
    // document.getElementById('parm2').value = ""
    // document.getElementById('lparm1').value = ""
    // document.getElementById('lparm2').value = ""
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'priod': priod,
        },
        url: '/pay/getPriod/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {

                if(resp.active===true){
			
                    alert('امکان ثبت اطلاعات برای این ماه هنوز باز نشده')
                    document.getElementById('btnview').style.display="none"
                     document.getElementById('sarane').innerText=""
                }else {
                    document.getElementById('btnview').style.display="block"

                }
            }
        },
    })
}


function FormatNumberBy3(num, decpoint, sep) {

    // check for missing parameters and use defaults if so
    if (arguments.length == 2) {
        sep = ",";
    }
    if (arguments.length == 1) {
        sep = ",";
        decpoint = ".";
    }
    // need a string for operations
    num = num.toString();
    // separate the whole number and the fraction if possible
    a = num.split(decpoint);
    x = a[0]; // decimal
    y = a[1]; // fraction
    z = "";


    if (typeof (x) != "undefined") {
        // reverse the digits. regexp works from left to right.
        for (i = x.length - 1; i >= 0; i--)
            z += x.charAt(i);
        // add seperators. but undo the trailing one, if there
        z = z.replace(/(\d{3})/g, "$1" + sep);
        if (z.slice(-sep.length) == sep)
            z = z.slice(0, -sep.length);
        x = "";
        // reverse again to get back the number
        for (i = z.length - 1; i >= 0; i--)
            x += z.charAt(i);
        // add the fraction back in, if it was there
        if (typeof (y) != "undefined" && y.length > 0)
            x += decpoint + y;
    }

    return x;
}

function masterlist(obj, st, zone) {
    $('#SerialTable tbody').empty()
waiting()

    if (st === 1) {
        document.getElementById('headerid').innerText = "لیست سریال کارتخوان"
    } else {
        document.getElementById('headerid').innerText = "لیست سریال صفحه کلید"
    }

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'obj': obj,
            'st': st,
            'zone': zone,
        },
        url: '/pay/getMasterList/',
        dataType: "json",
        success: function (resp) {

            if (resp.message === "success") {
                var t = 1
                $('#SerialTable tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    var content = '';
                    content += '<tr>';
                    content += '<td>' + t + '</td>';
                    content += '<td>' + mlist.serial + '</td>';
                    if(mlist.level === 0){
                            content +='<td><img width="30px" src="/static/assets/img/risk/work-started-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته خرابی نداشته" alt=""/> </td>'
                        }
                    if(mlist.level === 1){
                            content +='<td><img width="30px" src="/static/assets/img/risk/low-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته یکبار معیوب شد" alt=""/> </td>'
                        }
                                 if(mlist.level === 2){
                            content +='<td><img width="30px" src="/static/assets/img/risk/medium-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته دو بار معیوب شد" alt=""/> </td>'
                        }
                                              if(mlist.level === 3){
                            content +='<td><img width="30px" src="/static/assets/img/risk/high-risk-alert-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته بیش از دو بار معیوب شد" alt=""/> </td>'
                        }
                    content += '<td>' + mlist.status + '</td>';
                    content += '<td><a data-toggle="tooltip" title="مشاهده سابقه قطعه" class="fa fa-search" href="/pay/historylist/'+mlist.serial+'"></a></td>';





                    content += '</tr>';
                    t += 1
                    $('#SerialTable tbody').append(content);


                }
            }
            ending();
        },
         error: function (xhr, status, error) {
            ending(1,error);
            $('#SerialTable tbody').empty()
         }
    })
}

function masterlisttek(obj, st, nomrator ) {
waiting()

    if (st === 1) {
        document.getElementById('headerid').innerText = "لیست سریال کارتخوان"
    } else {
        document.getElementById('headerid').innerText = "لیست سریال صفحه کلید"
    }

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'obj': obj,
            'st': st,
            'nomrator': nomrator,
        },
        url: '/pay/getMasterListtek/',
        dataType: "json",
        success: function (resp) {

            if (resp.message === "success") {
                var t = 1
                $('#SerialTable tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    var content = '';
                    content += '<tr>';
                    content += '<td>' + t + '</td>';
                    content += '<td>' + mlist.serial + '</td>';
                    content += '<td>' + mlist.tarikh + '</td>';
                    content += '<td>' + mlist.status + '</td>';
                    content += '</tr>';
                    t += 1
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






function getInformation(val) {
waiting()

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'val': val,
        },
        url: '/pay/getInformation/',
        dataType: "json",
        success: function (resp) {
            $('#myTable2 tbody').empty()
            if (resp.message === "success") {
                document.getElementById('id_gs').innerText = resp.count_gs
                document.getElementById('id_pump').innerText = resp.count_pump
                document.getElementById('id_ticket').innerText = resp.count_ticket
                document.getElementById('id_masternew').innerText = resp.count_master
                document.getElementById('id_pinpadnew').innerText = resp.count_pinpad
                document.getElementById('id_masterstore').innerText = resp.count_master_store
                document.getElementById('id_pinpadstore').innerText = resp.count_pinpad_store

                for (obj in resp.store) {
                    const mlist = resp.store[obj]
                    var content = '';

                    content += '<tr>';
                    content += '<td>' + mlist.taikhtakhsis + '</td>';
                    content += '<td>' + mlist.storage + '</td>';
                    content += '<td>' + mlist.master + '</td>';
                    content += '<td>' + mlist.pinpad + '</td>';
                    content += '<td>' + mlist.status + '</td>';
                    content += '<td>' + mlist.tarikhmarsole + '</td>';
                    content += '<td>' + mlist.resid_date + '</td>';
                    content += '</tr>';

                    $('#myTable2 tbody').append(content);
                    ending();
                }
            }
        },
         error: function (xhr, status, error) {
            ending(1,error);
         }
    })
}

function updateItempay(val,id) {


        var newval = document.getElementById('item_info').value

waiting()

    $.ajax({
        cache: false,
        url: "/api/set-marsole",
        data: {
            val: val,
            id: id,
            newval: newval,
        },
        success: function (data) {


                      if (data.val === 61) {
                document.getElementById('marsole_Id'+id).innerText = data.newname
            }
            alarm('success', 'اطلاعات  بروزرسانی شد')
           ending();
        },
        error: function (xhr, status, error) {
           ending();



        }
    });
}


function masterlistresid(obj, st, zone) {
    $('#SerialTable tbody').empty()
    waiting()

    if (st === 1) {
        document.getElementById('headerid').innerText = "لیست سریال کارتخوان"
    } else {
        document.getElementById('headerid').innerText = "لیست سریال صفحه کلید"
    }

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'obj': obj,
            'st': st,
            'zone': zone,
        },
        url: '/pay/getmasterresid/',
        dataType: "json",
        success: function (resp) {

            if (resp.message === "success") {
                var t = 1
                $('#SerialTable tbody').empty()
                for (obj in resp.list) {
                    const mlist = resp.list[obj]
                    var content = '';
                    content += '<tr>';
                    content += '<td>' + t + '</td>';
                    content += '<td>' + mlist.serial + '</td>';
                    content += '<td>' + mlist.statusstore + '</td>';
                    if(mlist.level === 0){
                            content +='<td><img width="30px" src="/static/assets/img/risk/work-started-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته خرابی نداشته" alt=""/> </td>'
                        }
                    if(mlist.level === 1){
                            content +='<td><img width="30px" src="/static/assets/img/risk/low-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته یکبار معیوب شد" alt=""/> </td>'
                        }
                                 if(mlist.level === 2){
                            content +='<td><img width="30px" src="/static/assets/img/risk/medium-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته دو بار معیوب شد" alt=""/> </td>'
                        }
                                              if(mlist.level === 3){
                            content +='<td><img width="30px" src="/static/assets/img/risk/high-risk-alert-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته بیش از دو بار معیوب شد" alt=""/> </td>'
                        }
                    content += '<td>' + mlist.status + '</td>';
                    content += '<td><a data-toggle="tooltip" title="مشاهده سابقه قطعه" class="fa fa-search" href="/pay/historylist/'+mlist.serial+'"></a></td>';
                                        if(mlist.input === "1"){
                            content +='<td><img width="30px" src="/static/assets/img/add.png" data-toggle="tooltip" title="قطعه با فایل اکسل اضافه شد" alt=""/> </td>'
                        }
                                        if(mlist.input === "2"){
                            content +='<td><img width="30px" src="/static/assets/img/blue-check-mark-icon.png" data-toggle="tooltip" title="قطعه با فایل اکسل رسید شد" alt=""/> </td>'
                        }

                                        if(mlist.input === "3"){
                            content +='<td><img width="30px" src="/static/assets/img/fail-icon.png" data-toggle="tooltip" title="مغایرت" alt=""/> </td>'
                        }
                                        if(mlist.input === "-"){
                            content +='<td>-</td>'
                        }




                    content += '</tr>';
                    t += 1
                    $('#SerialTable tbody').append(content);


                }
            }
            ending();
        },
         error: function (xhr, status, error) {
            ending(1,error);
            $('#SerialTable tbody').empty()
         }
    })
}