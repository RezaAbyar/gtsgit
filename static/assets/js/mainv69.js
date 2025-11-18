const TitelId = document.getElementById('id_failure');
const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
const gId = document.getElementById('id_gs');
const checkId = document.getElementById('checkid');
const modal = document.getElementById("workflowModal");


function GETFailures() {
    const Tid = document.getElementById('id_failure').value
    waiting();

    let url = '/subFailure/';

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'Tid': Tid,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
        } else {


            if (resp.ok === 1) {
                document.getElementById('showNazel').style.display = "block";


            } else {
                document.getElementById('showNazel').style.display = "none";
            }
        }
        ending();

    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;
}

function getStore(id, store) {

    waiting();
    pump = document.getElementById('pumpId').value

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': store,
            'StoreId': id,
            'pump': pump,
        },
        url: '/pay/getStoreTek/',
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === 'success') {
            var content = '';


            if (resp.serial !== 0) {
                document.getElementById('id_daghi').value = resp.serial
                document.getElementById('id_daghi').readOnly = true;
            } else {
                document.getElementById('id_daghi').readOnly = false;
                document.getElementById('id_daghi').value = "";
            }
            $('#id_init').empty()
            for (obj in resp.list) {
                const mlist = resp.list[obj]
                content += '<option value=' + mlist.id + '>' + mlist.serial + '</option>'
            }
            $('#id_init').append(content)


        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function getStorestart(id, store) {
    waiting();
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'id': store,
            'StoreId': id,

        },
        url: '/pay/getStoretoTek/',
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === 'success') {
            var content = '';


            $('#id_init').empty()
            for (obj in resp.list) {
                const mlist = resp.list[obj]
                content += '<option value=' + mlist.id + '>' + mlist.serial + '</option>'
            }
            $('#id_init').append(content)
            document.getElementById('refreshBtn').style.display = "none";
            ending();
        }
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function GETCustomer() {
    waiting();
    gsid = gId.value


    let url = '/loadNazel/'
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'gId': gsid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
        } else {
            document.getElementById('id_lat').value = resp.lat
            document.getElementById('id_lon').value = resp.lon
            $('#ListTicketId').empty()
            for (obj in resp.ticketlist) {

                content += '<div class="row"><div class="col-lg-12 col-md-12 col-sm-12"><div class="card border">  <div class="card-body"><div class="row"><div class="col-lg-4 col-md-6 col-12 col-sm-6">'
                content += '<p class="mb-0">' + resp.ticketlist[obj].failure + ' </p>'
                if (resp.ticketlist[obj].pump > 0) {
                    content += '<p class="small text-muted mb-1 mt-1 line-height-18">  نازل ' + resp.ticketlist[obj].pump + ' </p>'
                }
                content += '</div><div class="col-lg-4 col-md-6 col-6 col-sm-6"><figure class="avatar mr-3">'

                if (resp.ticketlist[obj].oid === 1) {
                    content += '<div class="badge badge-primary">'
                }
                if (resp.ticketlist[obj].oid === 2) {
                    content += '<div class="badge badge-warning">'
                }
                if (resp.ticketlist[obj].oid === 3) {
                    content += '<div class="badge badge-success">'
                }
                if (resp.ticketlist[obj].oid === 4) {
                    content += '<div class="badge badge-danger">'
                }
                if (resp.ticketlist[obj].oid === 5) {
                    content += '<div class="badge badge-danger">'
                }
                if (resp.ticketlist[obj].oid === 6) {
                    content += '<div class="badge badge-danger">'
                }


                content += 'ارجاع به ' + resp.ticketlist[obj].organization + '  </div></figure></div>'
                content += '<div class="col-lg-2 col-md-3 col-3 col-sm-12"><button onclick="getWorkflow(' + resp.ticketlist[obj].id + ')" class="btn btn-light" ></i><span>پیگیری</span></button></div>'
                // if (resp.ticketlist[obj].isdel === 1) {
                //     content += '<div class="col-lg-2 col-md-36 col-3 col-sm-12"><a class="btn btn-danger" href="/deleteticket/' + resp.ticketlist[obj].id + '">حذف</a></div>'
                // }
                content += '</div></div></div>'
            }
            $('#ListTicketId').append(content);
            content = '';


            $('#id_Pump').empty()
            content += '<option value=0>یک نازل را انتخاب کنید </option>'
            for (obj in resp.mylist) {
                content += '<option value=' + resp.mylist[obj].id + '>نازل  ' + resp.mylist[obj].number + ' - ' + resp.mylist[obj].product + ' </option>'
            }
            $('#id_Pump').append(content);


        }
        getweather();
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;
}

//
// SaveTicketBtn.addEventListener('change', function () {
//     var addgId=gId.value
//     var addTitelId=TitelId.value
//     var nazelid = document.getElementById('').value
//
//     var $this = $(this);
//     let url = '/subFailure/'
//     var content = '';
//     $.ajax({
//         type: 'POST',
//         data: {
//             'csrfmiddlewaretoken': csrf,
//             'Tid': Tid,
//
//         },
//         url: url,
//         dataType: "json",
//         success: function (resp) {
//             if (resp.message === "success") {
//             } else {
//
//
//             if(resp.ok === 1){
//                     document.getElementById('showNazel').style.display = "block";
//
//
//            }else {
//                 document.getElementById('showNazel').style.display = "none";
//             }
//             }
//         }
//     });
//     return false;
// });
//
//
// });
function getWorkflow(obj) {
    waiting();
    document.getElementById('ticketId').value = obj
    let url = '/getWorkflow/'
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'obj': obj,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {

        if (resp.msg.length > 1) {
            alarm('error', resp.msg)
            return false
        } else {

            $('#ListTicketId').empty()
            content += '<div class="timeline">'
            for (obj in resp.mylist) {

                content += '<div class="timeline-item"><div class="timeline-item"><div><figure class="avatar avatar-sm mr-3 bring-forward"><span class="avatar-title bg-success-bright text-success rounded-circle">' + resp.mylist[obj].count + '</span></figure></div>'

                content += '<div><h6 class="d-flex justify-content-between mb-4 primary-font">'

                if (obj === '0') {
                    content += '<a href="#">' + resp.mylist[obj].name + '</a> ایجاد تیکت</span>'
                } else {
                    content += '<a href="#">' + resp.mylist[obj].name + '</a> ارجاع به  ' + resp.mylist[obj].org + '</span>'
                }
                content += '<span class="text-muted font-weight-normal" title="test" data-toggle="tooltip">' + resp.mylist[obj].date + '  (' + resp.mylist[obj].time + ')</span></h6>'
                if (resp.mylist[obj].info.length > 0) {
                    content += '<a href="#"><div class="mb-3 border p-3 border-radius-1"> ' + resp.mylist[obj].info + '</div> </a>'
                }

                if (resp.mylist[obj].s_master.length > 0) {
                    content += '<label><div class="badge badge-info border-radius-1"> کارتخوان نصب شده' + resp.mylist[obj].s_master + '</div> </label>'
                    content += '<label><div class="badge badge-danger border-radius-1"> کارتخوان داغی' + resp.mylist[obj].s_master_daghi + '</div> </label>'
                }

                if (resp.mylist[obj].s_pinpad.length > 0) {
                    content += '<label><div class="badge badge-info border-radius-1"> صفحه کلید نصب شده' + resp.mylist[obj].s_pinpad + '</div> </label>'
                    content += '<label><div class="badge badge-danger border-radius-1"> صفحه کلید داغی' + resp.mylist[obj].s_pinpad_daghi + '</div> </label>'
                }
                content += '</div> </div> </div>'
            }
            content += '</div><button style="display: block" id="backid" class="btn btn-light-warning" onclick="loadTikets(' + resp.mylist[obj].gs + ')">بازگشت </button>'
            $('#ListTicketId').append(content);
            $('#ticketTitel').empty()
            $('#ticketTitel').append('<h6> پیگیری</h6>')
        }
        ending();

    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;

}

function loadTikets(obj) {
    waiting();

    gsid = obj
    $(this);
    let url = '/loadNazel/'
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'gId': gsid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
        } else {
            $('#ListTicketId').empty()
            for (obj in resp.ticketlist) {

                content += '<div class="row"><div class="col-lg-12 col-md-12 col-sm-12"><div class="card border">  <div class="card-body"><div class="row"><div class="col-lg-4 col-md-6 col-12 col-sm-6">'
                content += '<p class="mb-0">' + resp.ticketlist[obj].failure + ' </p>'
                if (resp.ticketlist[obj].pump > 0) {
                    content += '<p class="small text-muted mb-1 mt-1 line-height-18">  نازل ' + resp.ticketlist[obj].pump + ' </p>'
                }
                content += '</div><div class="col-lg-4 col-md-6 col-6 col-sm-6"><figure class="avatar mr-3">'

                if (resp.ticketlist[obj].oid === 1) {
                    content += '<div class="badge badge-primary">'
                }
                if (resp.ticketlist[obj].oid === 2) {
                    content += '<div class="badge badge-warning">'
                }
                if (resp.ticketlist[obj].oid === 3) {
                    content += '<div class="badge badge-success">'
                }
                if (resp.ticketlist[obj].oid === 4) {
                    content += '<div class="badge badge-danger">'
                }
                if (resp.ticketlist[obj].oid === 5) {
                    content += '<div class="badge badge-danger">'
                }
                if (resp.ticketlist[obj].oid === 6) {
                    content += '<div class="badge badge-danger">'
                }
                content += 'ارجاع به ' + resp.ticketlist[obj].organization + '  </div></figure></div>'
                content += '<div class="col-lg-4 col-md-6 col-6 col-sm-12"><button onclick="getWorkflow(' + resp.ticketlist[obj].id + ')" class="btn btn-light" ></i><span>پیگیری</span></button></div></div></div></div>'
            }
            $('#ListTicketId').append(content);
            content = '';
            $('#ticketTitel').empty()
            $('#ticketTitel').append('<h6>  لیست تیکت های در حال بررسی شما</h6>')

            document.getElementById('refreshBtn').style.display = "none";

        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function Getwork(obj1, a, b, rnd) {

    waiting();

    document.getElementById('ticketId').value = obj1

    if (a === 1) {
        if (b === 7) {
            getLock(obj1)
        }
        if (b === 8) {
            getLock(obj1)
        }
    }
    $(this);
    let url = '/getWorkflow/'
    var content = '';

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'obj': obj1,
            'rnd': rnd,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        document.getElementById('workflowModal').style.display = "blank"
        if (resp.msg.length > 1) {
            document.getElementById('workflowModal').style.display = "none"
            $('#workflowModal').modal("hide");
            $('.modal-backdrop').hide();


            alarm('error', resp.msg)


            ending()

            return false
        }
        if (resp.message === "no") {

            $('#workflowModal').empty()
            alarm('error', 'شما یک داغی ثبت نشده دارید ابتدا باید در فرم ثبت داغی آن را ثبت کنید')

        } else {

            document.getElementById('address').value = resp.myticket[0].address
            document.getElementById('headerid').innerHTML = '<input type="hidden" id="orjfailur" value="' + resp.myticket[0].fid + '"> <h5 class="modal-title" id="exampleModalCenterTitle">شماره تیکت : ' + resp.myticket[0].id + ' - شرح: ' + resp.myticket[0].info + ' </h5><button type="button" class="close" data-dismiss="modal" aria-label="Close"><i class="ti-close" aria-hidden="true"></i></button>'
            // content += '<h6> جایگاه  :  ' + resp.myticket[0].gsid + ' - ' + resp.myticket[0].gsname + '</h6>'
            content += '<div class="btn-group" role="group" aria-label="Basic example"> <button type="button" class="btn btn-primary" onclick="gsinformation(' + resp.myticket[0].id + ')">  <i class="fa fa-info-circle" aria-hidden="true"> </i></button></span><a type="button" class="btn btn-success" href="/gs_detail/' + resp.myticket[0].gs_id + '"> ' + resp.myticket[0].gsid + ' - ' + resp.myticket[0].gsname + '</a></div></div></div></div>'


            if (resp.myticket[0].nazel === '-') {
            } else {
                document.getElementById('GsId').value = resp.myticket[0].gsid
                document.getElementById('NazelId').value = resp.myticket[0].nazel
                // content += ' <a onclick="editItem(5,{{ gs.id }})" href="#" class="btn btn-outline-light ml-2"\n' +
                //     '                                           title="" data-toggle="modal" data-target="#editMenu"\n' +
                //     '                                           data-original-title="ویرایش وظیفه">\n' +
                //     '                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"\n' +
                //     '                                                 viewBox="0 0 24 24"\n' +
                //     '                                                 fill="none" stroke="currentColor" stroke-width="2"\n' +
                //     '                                                 stroke-linecap="round"\n' +
                //     '                                                 stroke-linejoin="round" class="feather feather-edit-3">\n' +
                //     '                                                <path d="M12 20h9"></path>\n' +
                //     '                                                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>\n' +
                //     '                                            </svg>\n' +
                //     '                                        </a>'
                content += '<a class="btn btn-warning" href="/RoleTickets/?gs=' + resp.myticket[0].gs_id + '&pump=' + resp.myticket[0].nazel_id + '"> نازل :  ' + resp.myticket[0].nazel + '</a>'
            }
            content += '<a class="btn btn-info" data-toggle="tooltip" title="' + resp.myticket[0].tektell + '" href="tel:' + resp.myticket[0].tektell + '" > تکنسین :  ' + resp.myticket[0].tek + '</a>'
            if (resp.myticket[0].nazel === '-') {
            } else {
                content += '<h6 id="serialmasterdaghi">' + resp.myticket[0].serialmaster + '</h6>'
                content += '<h6 id="serialpinpaddaghi">' + resp.myticket[0].serialpinpad + '</h6>'
                if (resp.myticket[0].isclose === 1 && resp.nextsell > 0) {

                    content += '<div class="alert alert-warning alert-with-border" role="alert"> <strong>  نازل پس از ثبت تیکت دارای ' + resp.nextsell + ' روز فروش میباشد </strong></div>'

                }

            }

            document.getElementById('gsidid').innerHTML = content


            content = ""
            $('#ListTicketId').empty()
            content += '<div class="row">'
            content += '<div class="col-12">'
            content += '<div class="timeline">'
            content += '<div class="row">'
            content += '<div class="col-12">'

            for (obj in resp.mylist) {
                if ((resp.mylist[obj].lat).length > 2) {
                    content += '<input type="hidden" id="latshow' + obj + '" value="' + resp.mylist[obj].metr + '">'
                    if (resp.isboarder) {
                        content += '<div style="padding:8px;border:3px solid lightblue;" class="form-group"> <a onclick="showPosition(' + resp.mylist[obj].long + ',' + resp.mylist[obj].lat + ',' + resp.mylist[obj].latto + ',' + resp.mylist[obj].longto + ',' + obj.toString() + ')" href="#" data-toggle="tooltip" title="' + resp.mylist[obj].metr + ' "><div class="timeline-item"><div class="timeline-item"><div><figure   class="avatar avatar-sm mr-3 bring-forward"><span  class="avatar-title bg-primary-bright text-primary rounded-circle">' + resp.mylist[obj].count + '</span></figure></div></a>'
                    } else {
                        content += '<div  class="form-group"> <a onclick="showPosition(' + resp.mylist[obj].long + ',' + resp.mylist[obj].lat + ',' + resp.mylist[obj].latto + ',' + resp.mylist[obj].longto + ',' + obj.toString() + ')" href="#"><div class="timeline-item"><div class="timeline-item"><div><figure   class="avatar avatar-sm mr-3 bring-forward"><span  class="avatar-title bg-primary-bright text-primary rounded-circle">' + resp.mylist[obj].count + '</span></figure></div></a>'
                    }
                } else {
                    if (resp.isboarder) {
                        content += '<div style="padding:8px;border:3px solid lightblue;" class="form-group"> <div  class="timeline-item"><div class="timeline-item"><div><figure class="avatar avatar-sm mr-3 bring-forward"><span  class="avatar-title bg-success-bright text-success rounded-circle">' + resp.mylist[obj].count + '</span></figure></div>'
                    } else {
                        content += '<div  class="form-group"> <div  class="timeline-item"><div class="timeline-item"><div><figure class="avatar avatar-sm mr-3 bring-forward"><span  class="avatar-title bg-success-bright text-success rounded-circle">' + resp.mylist[obj].count + '</span></figure></div>'
                    }
                }

                if (resp.mylist[obj].phone !== '-') {
                    content += '<divz><h6 class="d-flex justify-content-between mb-4 primary-font"><span  title="' + resp.mylist[obj].role + '" data-toggle="tooltip">' + resp.mylist[obj].name + '</span>  <a data-toggle="tooltip" title="' + resp.mylist[obj].phone + '"  href="tel:' + resp.mylist[obj].phone + '"> &nbsp&nbsp <span class="fa fa-phone"></span> &nbsp&nbsp </a><span  data-toggle="tooltip"> ' + resp.mylist[obj].role + '</span></h6>'
                } else {
                    content += '<divz><h6 class="d-flex justify-content-between mb-4 primary-font"><span  title="' + resp.mylist[obj].role + '" data-toggle="tooltip">' + resp.mylist[obj].name + '</span> &nbsp | &nbsp<span  data-toggle="tooltip"> ' + resp.mylist[obj].role + '</span></h6>'
                }
                content += '</div>'
                content += '<figure class="avatar avatar-sm mr-3 bring-forward"><span data-toggle="tooltip" title="رویداد کاربران" onclick="geteventslogs(' + resp.mylist[obj].id + ')"  class="avatar-title bg-warning-bright  rounded-circle fa fa-list"></span></figure>'
                content += '</div>'

                content += '<div class="row">'

                content += '<div class="col-12">'
                if (resp.mylist[obj].oid === 1) {
                    content += '<div class="bg bg-primary">'
                }
                if (resp.mylist[obj].oid === 2) {
                    content += '<div class="bg bg-warning">'
                }
                if (resp.mylist[obj].oid === 3) {
                    content += '<div class="bg bg-success">'
                }
                if (resp.mylist[obj].oid === 4) {
                    content += '<div class="bg bg-danger">'
                }
                if (resp.mylist[obj].oid === 5) {
                    content += '<div class="bg bg-danger">'
                }
                if (resp.mylist[obj].oid === 6) {
                    content += '<div class="bg bg-danger">'
                }
                if (parseInt(resp.mylist[obj].oid) > 6) {
                    content += '<div class="bg bg-twitter">'
                }
                content += '<span class="bg bg-dark">'
                content += ' ارجاع به ' + resp.mylist[obj].org + ' </span>'

                content += '<span  style="color: #f5ca83; background: #3f3d3d" title="' + resp.mylist[obj].macaddress + '"  data-toggle="tooltip" ondblclick="alert(' + resp.mylist[obj].macaddress + ')">' + resp.mylist[obj].date + '  (' + resp.mylist[obj].time + ')</span>'

                if (resp.mylist[obj].status === 2) {
                    if (parseInt(resp.mylist[obj].counter) === parseInt(obj)) {
                        content += '<div class="bg bg-dribbble">'
                        content += ' تیکت بسته شد '
                        // content += '</div>'
                    } else {
                        content += '<h6>' + resp.mylist[obj].failure + '</h6> </div>'
                    }
                } else {
                    content += '<h6>' + resp.mylist[obj].failure + '</h6> </div>'
                }

                if (resp.mylist[obj].newtime) {
                    content += '<div class="alert alert-danger alert-with-border" role="alert"><strong>  </strong><span style="font-size: 20px">' + resp.mylist[obj].metr + '</span>  ، در صورت مغایرت و حضور شما درجایگاه برای دریافت مجدد لوکیشن   <a class="btn btn-outline-danger" onclick="getGPS(' + resp.mylist[obj].id + ')"  href="#"> اینجا کلیک کنید</a></div>'
                }
                content += '</div></div>'

                content += '<div class="row">'
                content += '<div class="col-12">'

                if (resp.mylist[obj].info.length > 0) {
                    content += '<a><div style="background: rgba(243,241,241,0.79);color:#0b0b0b" class="mb-3 border p-3 border-radius-1"> ' + resp.mylist[obj].info + ''
                    if (resp.mylist[obj].s_master.length > 0 || resp.mylist[obj].s_pinpad.length > 0) {
                        content += '<hr>'
                    }

                    if (resp.mylist[obj].s_master.length > 0) {
                        content += '<button onclick="storehistory(' + resp.mylist[obj].s_master + ')" class="badge badge-dark">    نصب ' + "  " + resp.mylist[obj].s_master + '</button>  '
                        if (resp.mylist[obj].s_master_daghi.length > 0) {
                            content += '<button onclick="storehistory(' + resp.mylist[obj].s_master_daghi + ')" class="badge badge-danger">      داغی' + "  " + resp.mylist[obj].s_master_daghi + '</button>  '
                        }
                    }
                    if (resp.mylist[obj].s_pinpad.length > 0) {
                        content += '<button onclick="storehistory(' + resp.mylist[obj].s_pinpad + ')" class="badge badge-dark">    نصب ' + "  " + resp.mylist[obj].s_pinpad + '</button>  '
                        if (resp.mylist[obj].s_pinpad_daghi.length > 0) {
                            content += '<button onclick="storehistory(' + resp.mylist[obj].s_pinpad_daghi + ')" class="badge badge-danger">    داغی' + "  " + resp.mylist[obj].s_pinpad_daghi + '</button>  '
                        }
                    }

                    content += ' </div> </a>'

                } else {
                    if (resp.mylist[obj].s_master.length > 0 || resp.mylist[obj].s_pinpad.length > 0) {
                        content += '<a><div style="background: rgba(243,241,241,0.79);color:#0b0b0b" class="mb-3 border p-3 border-radius-1">'
                    }
                    if (resp.mylist[obj].s_master.length > 0) {

                        content += '<button onclick="storehistory(' + resp.mylist[obj].s_master + ')" class="badge badge-dark">   کارتخوان نصب شده' + "  " + resp.mylist[obj].s_master + '</button>  '
                        content += '<button onclick="storehistory(' + resp.mylist[obj].s_master_daghi + ')" class="badge badge-warning">   کارتخوان داغی' + "  " + resp.mylist[obj].s_master_daghi + '</button>  '
                    }
                    if (resp.mylist[obj].s_pinpad.length > 0) {
                        content += '<button onclick="storehistory(' + resp.mylist[obj].s_pinpad + ')" class="badge badge-dark">   صفحه کلید نصب شده' + "  " + resp.mylist[obj].s_pinpad + '</button>  '
                        content += '<button onclick="storehistory(' + resp.mylist[obj].s_pinpad_daghi + ')" class="badge badge-warning">   صفحه کلید داغی' + "  " + resp.mylist[obj].s_pinpad_daghi + '</button>  '
                    }
                    if (resp.mylist[obj].s_master.length > 0 || resp.mylist[obj].s_pinpad.length > 0) {
                        content += ' </div> </a>'
                    }
                    content += '<dialog id="cadrstore"></dialog><br>'
                }

                content += '</div></div></div>'
            }
            content += '</div> </div> </div></div>'

            $('#ListTicketId').append(content);
            ending();
            $('#fotterid').empty()
            content = ""

            if (resp.formpermmision === 1) {
                if (resp.access === '1') {
                    if ((document.getElementById("id_latid").value).length > 2 || document.getElementById("id_ownerrole").value === "1" || resp.isgps === false) {
                        content += ' <button onclick="getForward()" type="button" class="btn btn-outline-warning btn-pulse">ارجاع</button>'
                        var urlq;
                        if (resp.ending === 1) {
                            if (resp.isgps === false) {
                                urlq = "../sell/acceptrpmqrcode/" + obj1 + "/1/1/" + resp.myticket[0].fid + "/"
                            } else {
                                urlq = "../sell/acceptrpmqrcode/" + obj1 + "/" + document.getElementById("id_latid").value + "/" + document.getElementById("id_lngid").value + "/" + resp.myticket[0].fid + "/"
                            }
                            if (resp.closebyqrcode) {
                                content += ' <a id="a"  href="' + urlq + '" type="button" class="btn btn-outline-success btn-pulse">رسیدگی</a>'


                            } else {
                                content += ' <button id="checkid" onclick="getok()" type="button" class="btn btn-outline-success btn-pulse">رسیدگی</button>'
                            }
                        } else {
                            alarm('warning', 'این تیکت  پس از تایید توسط ' + resp.end_vahed + '  بسته میشود(شما پس از از بررسی با ثبت شرح کامل اقدامات به آن واحد ارجاع بدهید.')
                        }

                    } else {
                        alarm('warning', 'لوکیشن تلفن همراه خود را روشن کنید و دسترسی به لوکیشن را بررسی کنید')
                    }
                } else {
                    alarm('warning', 'تیکت در اختیار شما نیست امکان بستن یا ارجاع برای شما وجود ندارد')
                }
            }
        }
        content += ' <button type="button" class="btn btn-secondary" data-dismiss="modal">بستن</button>'
        $('#fotterid').append(content);

        ending();


    })
        .fail(function (xhr, status, error) {


            ending(1, error)

        })
    return false;
}

function getok() {
    waiting();
    tid = document.getElementById('ticketId').value
    $(this);
    let url = '/closeTicket/'
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'obj': tid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
        } else {
            if (resp.s_master != 0) {

                checkrisk(resp.s_master)
            }
            content = ""
            $('#ListTicketId').empty()
            if (resp.editable) {
                content += '<label for="SarfaslId">سرفصل</label>'
                content += '<select id="SarfaslId" onchange="sarfaslIDedit()" class="select3-example">'

                for (obj in resp.failurcat) {

                    if (resp.failurcat[obj].id === resp.mycat) {
                        content += '<option selected '
                    } else {
                        content += '<option '
                    }
                    content += 'value=' + resp.failurcat[obj].id + '>' + resp.failurcat[obj].info + '</option>'
                }
                content += '</select>'
            }
            content += '<label for="validationCustom02">موضوع</label>'
            if (resp.editable) {
                content += '<select id="id_failure" class="select3-example">'
            } else {
                content += '<select id="id_failure" class="select3-example" disabled>'
            }

            for (obj in resp.failursub) {

                if (resp.failursub[obj].id === resp.myfailur) {
                    content += '<option selected '
                } else {
                    content += '<option '
                }
                content += 'value=' + resp.failursub[obj].id + '>' + resp.failursub[obj].info + '</option>'
            }
            content += '</select>'


            content += '<label for="validationCustom02">شرح اقدام</label>'
            content += '<select  onchange="getReplyischange()" id="rpId" class="select3-example">'
            content += '<option value=0>یک اقدام انتخاب کنید</option>'
            for (obj in resp.replydic) {
                content += '<option value=' + resp.replydic[obj].id + '>' + resp.replydic[obj].info + '</option>'
            }
            content += '</select>'
        }
        content += '<div id="changecart"></div>'
        content += '<div id="peykarbandi"></div>'
        content += '<label for="validationCustom02">توضیحات</label>'
        content += '<textarea  class="form-control" id="InfooIdClose" placeholder=""</textarea>'


        $('#ListTicketId').append(content);
        $('#fotterid').empty()
        content = ""
        content += ' <button onclick="getCloseTicket()" type="button" id="CloseBtnId" class="btn btn-success btn-pulse" data-dismiss="modal"> <i id="CloseBtnIdspan" style="display: none" class="fa fa-spinner fa-spin"></i>بستن تیکت</button>'
        content += ' <button type="button" class="btn btn-secondary" data-dismiss="modal">بستن</button>'
        $('#fotterid').append(content);

        $('.select3-example').select2({
            placeholder: 'Select'
        });
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;
}

function getForward() {
    waiting();
    tid = document.getElementById('ticketId').value
    $(this);
    let url = '/getForward/'
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'tid': tid,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
        } else {
            content = ""
            $('#ListTicketId').empty()
            if (resp.editable) {
                content += '<div class="col-12">\n' +
                    '                                    <div class="form-group">\n' +
                    '                                        <div class="custom-control custom-checkbox custom-checkbox-success">\n' +
                    '                                            <input type="checkbox" class="custom-control-input" id="showsarfasl"\n' +
                    '                                                   onclick="myFunction()">\n' +
                    '                                            <label class="custom-control-label" for="showsarfasl">ویرایش علت خرابی\n' +
                    '</label>\n' +
                    '                                        </div>\n' +
                    '                                    </div>'
                content += '<div style="display: none" id="ch_f">'
                content += '<label id="faillbl"  for="id_failure"> تغییر عنوان</label>'
                content += '<select style="display: none" id="id_failure" name="id_failure" class="select2-example">'
                content += '<option value="0">یک عنوان را انتخاب کنید..</option>'
                for (obj in resp.onvanlist) {
                    content += '<option value=' + resp.onvanlist[obj].id + '>' + resp.onvanlist[obj].info + '</option>'
                }
                content += '</select>'
                content += '</div>'
            }
            content += '<div class="form-group"><label for="validationCustom02">واحد ارجاع</label>'
            content += '<select id="erjaunitId" class="form-control form-control-bg">'

            for (obj in resp.thislist) {
                content += '<option value=' + resp.thislist[obj].id + '>' + resp.thislist[obj].info + '</option>'
            }
            content += '</select></div>'

            if (resp.refid === 1) {
                content += '<div class="form-group"> <label for="validationCustom03">فوریت</label>'
                content += '<select id="foryatId" class="form-control form-control-bg">'
                content += '<option value=1>معمولی</option>'
                content += '<option value=2>فوری</option>'
                content += '<option value=3>آنی</option>'
                content += '</select></div>'
            }
        }
        content += '<div class="form-group"><label for="validationCustom02">علت ارجاع</label>'
        content += '<select class="form-control form-control-bg" id="rpId2">'
        content += '<option value=0>یک علت انتخاب کنید</option>'
        for (obj in resp.replydic) {
            content += '<option value=' + resp.replydic[obj].id + '>' + resp.replydic[obj].info + '</option>'
        }
        content += '</select></div>'

        content += '<textarea  class="form-control" name="erjainfoId" id="erjainfoId" placeholder=""</textarea>'


        $('#ListTicketId').append(content);
        $('#fotterid').empty()
        content = ""
        content += ' <button onclick="getForwardTicket()" type="button" class="btn btn-success btn-pulse" data-dismiss="modal">ثبت ارجاع</button>'
        content += ' <button type="button" class="btn btn-secondary" data-dismiss="modal">بستن</button>'
        $('#fotterid').append(content);
        document.getElementById('refreshBtn').style.display = "none";
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });

    return false;
}

function getCloseTicket() {

    waiting();
    var mytext = ""
    tid = document.getElementById('ticketId').value
    InfooIdClose = document.getElementById('InfooIdClose').value
    failurId = document.getElementById('id_failure').value
    InfooIdClose = document.getElementById('InfooIdClose').value
    rpId = document.getElementById('rpId').value
    mid = document.getElementById('ischangemasterid').value
    pid = document.getElementById('ischangepinpadid').value
    lat = document.getElementById('id_latid').value
    lang = document.getElementById('id_lngid').value
    if (failurId === "0") {
        alarm('warning', 'یک عنوان انتخاب کنید')
        ending();
        return false
    }
    if (rpId === "0") {
        alarm('warning', 'یک شرح اقدام انتخاب کنید')
        ending();
        return false
    }

    if (document.getElementById('serialmasterdaghi')) {
        serialmasterdaghi = document.getElementById('serialmasterdaghi').innerHTML
    } else {
        serialmasterdaghi = 0
    }
    if (document.getElementById('serialpinpaddaghi')) {
        serialpinpaddaghi = document.getElementById('serialpinpaddaghi').innerHTML
    } else {
        serialpinpaddaghi = 0
    }


    let autodaghi = 1

    if (mid === '1' || mid === '2') {

        if (mid === '1') {
            cmasterId = document.getElementById('cmasterId').value
        }
        if (mid === '2') {
            cmasterId = 0
        }
        if (serialmasterdaghi.length > 5) {
            mytext = "آیا شماره قطعه داغی " + serialmasterdaghi + " میباشد؟؟  ";
            if (confirm(mytext) == true) {
                autodaghi = 1
            } else {
                autodaghi = 0
            }
        } else {
            autodaghi = 0
            mytext = ""
        }
        document.getElementById("demo").value = mytext;

    } else {
        cmasterId = 0
    }

    if (pid === '1' || pid === '2') {
        if (pid === '1') {
            cpinpadId = document.getElementById('cpinpadId').value
        }
        if (pid === '2') {
            cpinpadId = 0
        }
        if (serialpinpaddaghi.length > 5) {
            mytext = "آیا شماره قطعه داغی " + serialpinpaddaghi + " میباشد؟؟  ";
            if (confirm(mytext) == true) {
                autodaghi = 1
            } else {
                autodaghi = 0
            }
        } else {
            autodaghi = 0
            mytext = ""
        }
        document.getElementById("demo").value = mytext;

    } else {
        cpinpadId = 0
    }

    if (mid === '1' && cmasterId.length < 3) {
        alarm('error', 'کاربر گرامی باید حتما یک قطعه به این تیکت اختصای بدهید *****عملیات نا موفق*****')
        ending();
        return false
    }

    if (pid === '1' && cpinpadId.length < 3) {
        alarm('error', 'کاربر گرامی باید حتما یک قطعه به این تیکت اختصای بدهید *****عملیات نا موفق*****')
        ending();
        return false
    }
    $(this);
    let url = '/getCloseTicket/'
    document.getElementById("CloseBtnIdspan").style.display = 'block';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'obj': tid,
            'InfooIdClose': InfooIdClose,
            'failurId': failurId,
            'rpId': rpId,
            'cmasterId': cmasterId,
            'cpinpadId': cpinpadId,
            'lat': lat,
            'lang': lang,
            'autodaghi': autodaghi,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
            alarm('success', 'تیکت با موفقیت بسته شد')
            $('#tr' + tid).remove()

            if (resp.dgi === 0) {
                alarm('warning', 'لطفا فورا نسبت به ثبت داغی این قطعه در فرم ثبت داغی اقدام کنید')
                window.open('https://gts.niopdc.ir/pay/changestore/')
            }
            if (resp.dgi === 1) {
                alarm('info', 'داغی کارتخوان بصورت سیستمی ثبت شد')
            }
            if (resp.dgi === 2) {
                alarm('info', 'داغی صفحه کلید بصورت سیستمی ثبت شد')
            }
            ending();
            document.getElementById("CloseBtnIdspan").style.display = 'none';
        } else {
            alarm('warning', 'یک شرح اقدام انتخاب کنید')
            ending();
            document.getElementById("CloseBtnIdspan").style.display = 'none';
        }

        ending();
        document.getElementById("CloseBtnIdspan").style.display = 'none';
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
            document.getElementById("CloseBtnIdspan").style.display = 'none';
        });
}

function getReplyischange() {
    waiting();
    tid = document.getElementById('rpId').value
    gsid = document.getElementById('GsId').value
    nazel = document.getElementById('NazelId').value
    ticketid = document.getElementById('ticketId').value
    $(this);
    let url = '/getReplyischange/'
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'obj': tid,
            'gsid': gsid,
            'nazel': nazel,
            'ticketid':ticketid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
        } else {

            if (resp.role === 'tek' && resp.otp_peykarbandi !== "1") {

                document.getElementById('peykarbandi').innerHTML = `
            <div class="alert alert-dark" role="alert"><h3> کد پیکربندی: ` + resp.otp_peykarbandi + `</h3></div> `
            } else {
                document.getElementById('peykarbandi').innerHTML = ``
            }


            content = ""
            $('#changecart').empty()

            if (resp.master === 1) {
                document.getElementById('ischangemasterid').value = 1


                content += '<br>'


                content += '<label for="validationCustom02">شماره سریال کارتخوان</label>'
                content += '<select onclick="checkrisk(this.value)"   class="select3-example" id="cmasterId" required>'
                for (obj in resp.masters) {
                    const mlist = resp.masters[obj]
                    if (obj == 0) {
                        checkrisk(mlist.id)
                    }
                    content += '<option value="' + mlist.id + '">' + mlist.serial + '</option>'
                }
                content += '</select>'

                content += '<div id="risket"></div>'

            } else {
                document.getElementById('ischangemasterid').value = 0
            }
            if (resp.master === 2) {
                document.getElementById('ischangemasterid').value = 2
            }
            if (resp.pinpad === 1) {
                document.getElementById('ischangepinpadid').value = 1


                content += '<br>'
                content += '<label for="validationCustom02">شماره سریال صفحه کلید</label>'
                content += '<select   class="select3-example" id="cpinpadId" required>'
                for (obj in resp.pinpads) {
                    const mlist = resp.pinpads[obj]
                    content += '<option value="' + mlist.id + '">' + mlist.serial + '</option>'
                }
                content += '</select>'
            } else {
                document.getElementById('ischangepinpadid').value = 0

            }
            if (resp.pinpad === 2) {
                document.getElementById('ischangepinpadid').value = 2
            }
            $('#changecart').append(content);

        }
        $('.select3-example').select2({
            placeholder: 'Select'
        });
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function getForwardTicket() {
    waiting();
    var sms = 'off'
    if (document.getElementById("sms")) {
        if (document.getElementById("sms").checked) {
            sms = 'on'
        } else {
            sms = 'off'
        }
    }
    tid = document.getElementById('ticketId').value
    const checkBox = document.getElementById("showsarfasl");
    erjaunitId = document.getElementById('erjaunitId').value
    erjainfoId = document.getElementById('erjainfoId').value
    rpId2 = document.getElementById('rpId2').value
    lat = document.getElementById('id_latid').value
    lang = document.getElementById('id_lngid').value
    if (document.getElementById("showsarfasl")) {
        if (checkBox.checked === true) {
            failureid = document.getElementById('id_failure').value
        } else {
            failureid = document.getElementById('orjfailur').value
        }
    } else {
        failureid = document.getElementById('orjfailur').value
    }
    if (document.getElementById("foryatId")) {

        foryat = document.getElementById('foryatId').value

    } else {

        foryat = 1
    }

    let url = '/getForwardTicket/'
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'obj': tid,
            'erjaunitId': erjaunitId,
            'erjainfoId': erjainfoId,
            'failureid': failureid,
            'rpId2': rpId2,
            'lat': lat,
            'lang': lang,
            'foryat': foryat,
            'sms': sms,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {

            content = ""
            $('#tofw' + tid).empty()
            if (resp.erjaunitId === '1') {
                content += '<div class="badge badge-primary">'
            }
            if (resp.erjaunitId === '2') {
                content += '<div class="badge badge-warning">'
            }
            if (resp.erjaunitId === '3') {
                content += '<div class="badge badge-success">'
            }
            if (resp.erjaunitId === '4') {
                content += '<div class="badge badge-danger">'
            }
            if (resp.erjaunitId === '5') {
                content += '<div class="badge badge-danger">'
            }
            if (resp.erjaunitId === '6') {
                content += '<div class="badge badge-danger">'
            }
            content += resp.name + '  </div>'
            $('#tofw' + tid).append(content)
            content = ""
            $('#tofailur' + tid).empty()
            content += resp.fail
            $('#tofailur' + tid).append(content)
            alarm('success', 'تیکت با موفقیت ارجاع شد')
            if (resp.isdel === 1) {
                $('#tr' + tid).remove()
            }
        } else {
            alarm('error', resp.message)

        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function myFunction() {
    var failure = document.getElementById('ch_f');
    const checkBox = document.getElementById("showsarfasl");
    $('.select2-example').select2({
        placeholder: 'Select'
    });

    if (checkBox.checked === true) {
        failure.style.display = "block";
    } else {
        failure.style.display = "none";
    }
}

function GetArea() {

    let selectElement = document.getElementById('id_zone')
    let selectedValues = Array.from(selectElement.selectedOptions)
        .map(option => option.value)


    $.ajax({
        type: 'GET',
        data: {
            'csrfmiddlewaretoken': csrf,
            'myTag': selectedValues.toString(),
        },
        dataType: "json",
        url: '/api/get-area-info/',
    }).done(function (data) {
        $('#id_area').empty()
        for (obj in data.mylist) {

            const mlist = data.mylist[obj]
            var content = '';
            content += '<option value=' + mlist.id + '>' + mlist.name + ' (' + mlist.zone + ')</option>'

            $('#id_area').append(content);

        }


    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}


function GetGs() {
    waiting();
    let selectElement = document.getElementById('id_area')
    let selectedValues = Array.from(selectElement.selectedOptions)
        .map(option => option.value)


    $.ajax({
        type: 'GET',
        data: {

            'myTag': selectedValues.toString(),
        },
        dataType: "json",
        url: '/api/get-gs-info/',
    }).done(function (data) {

        $('#id_gs').empty()
        for (obj in data.mylist) {

            const mlist = data.mylist[obj]
            var content = '';

            content += '<option value=' + mlist.id + '>' + mlist.name + ' (' + mlist.area + ')</option>';

            $('#id_gs').append(content);

        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });

}

function Getcatfailure() {
    waiting();
    let selectElement = document.getElementById('id_failurecategory')
    let selectedValues = Array.from(selectElement.selectedOptions)
        .map(option => option.value)


    $.ajax({
        type: 'GET',
        data: {
            'myTag': selectedValues.toString(),
        },
        dataType: "json",
        url: '/api/get-failure-info/',
    }).done(function (data) {
        $('#id_failuresub').empty()
        for (obj in data.mylist) {

            const mlist = data.mylist[obj]
            var content = '';
            content += '<option value=' + mlist.id + '>' + mlist.info + ' (' + mlist.failurecategory + ')</option>';

            $('#id_failuresub').append(content);

        }
        ending();
    })

        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function lockedrow(val) {
    waiting();
    id = document.getElementById('ticketId').value

    let url = '/api/set-lock/'

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,
            'id': id,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
            alarm('success', 'این تیکت در اختیار شما قرار داده شد')
        }
        if (resp.message === "no") {
            alarm('success', ' تیکت آزاد شد')
        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function getLock(val) {
    waiting();

    let url = '/api/get-lock/'

    $.ajax({
        type: 'GET',
        data: {

            'id': val,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "1") {
            if (resp.me === 1) {
                document.getElementById('customSwitch5').checked = true;
            } else {
                document.getElementById('customSwitch5').checked = false;
            }
            alarm('info', resp.payam)
        } else {
            document.getElementById('customSwitch5').checked = false;
        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function showPosition(lat, lng, latto, longto, _obj) {
    waiting()

    var address = document.getElementById('address').value
    $.ajax({
        type: 'GET',
        dataType: "json",
        url: "https://api.neshan.org/v5/reverse?lat=" + lat + "&lng=" + lng,
        headers: {"Api-Key": "service.cb6e1f04610d4f33b3e2f22e2e55061b"},
    }).done(function (data) {
        ending()
        swal({
            title: "لوکیشن: " + data.formatted_address + `( ${document.getElementById('latshow' + _obj).value} )`,
            text: "آدرس جایگاه : " + address,
            icon: "success",
            buttons: {
                confirm: 'مشاهده روی نقشه',
                cancel: 'انصراف'
            },

            dangerMode: true
        })
            .then(function (willDelete) {
                if (willDelete) {
                    var a = document.createElement('a');
                    a.target = "_blank";

                    if (latto == '0') {
                        a.href = "https://www.google.com/maps/place/" + lat + "," + lng + "?entry=ttu";
                    } else {
                        a.href = "https://neshan.org/maps/@" + lat + "," + lng + ",13.6z,0p/routing/car/origin/" + lat + "," + lng + "/destination/" + latto + "," + longto
                    }
                    a.click();


                } else {

                }
            });

    })
}

// function showPosition2() {
//     var img_url = "https://api.neshan.org/v2/static?key=service.078d771a6be1489487f12b4d7e7f6ea0&type=dreamy&zoom=13&center=27.210361,57.340641&width=1120&height=300&marker=red";
//
//     document.getElementById("mapholder").innerHTML = "<img alt='" + img_url + "' src='" + img_url + "'>";
// }

function sla(ticket_id, status_id) {
    waiting();
    let url = '/sla/'

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'ticket_id': ticket_id,
            'status_id': status_id,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        document.getElementById('tr' + ticket_id).remove()
        alarm('success', 'عملیات با موفقیت انجام شد')

        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function gsinformation(gsid) {

    waiting();
    let url = '/api/gsinformation/'

    $.ajax({
        type: 'GET',
        data: {

            'gsid': gsid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {

        swal({
            title: resp.gs[0].name,
            text:
                ' تاریخ اسکن رمزینه: ' + resp.gs[0].ramzine + " " +
                '\n' +
                ' آخرین ارتباط جایگاه: ' + resp.gs[0].endconnection + " " +
                '\n' +
                ' وضعیت اتصال سم: ' + resp.gs[0].sam + " " +
                '\n' +
                ' وضعیت ارتباط مودم: ' + resp.gs[0].cmodem + " " +
                '\n' +
                '  ارتباط با مرکز داده: ' + resp.gs[0].dc + " " +
                '\n' +
                '  نسخه لیست سیاه: ' + resp.gs[0].blacklist + " " +
                '\n' +
                '  نسخه آر پی ام: ' + resp.gs[0].rpm + " " +
                '\n' +
                '  نسخه ایمیج: ' + resp.gs[0].img + " " +
                '\n' +
                ' نوع مودم: ' + resp.gs[0].modem + " " +
                '\n' +
                ' نوع سرور: ' + resp.gs[0].ipc + " " +
                '\n' +
                '  وضعیت جایگاه: ' + resp.gs[0].status + " "

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


function geteventslogs(wid) {

    waiting();
    let url = '/api/geteventslogs/'

    $.ajax({
        type: 'GET',
        data: {

            'wid': wid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var content = ''
        for (obj in resp.gs) {
            content += resp.gs[obj].owner + " | " + resp.gs[obj].tarikh +
                '\n'
        }


        swal({
            text:
            content

        })
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });


}

function storehistory(val) {
    waiting();


    let url = '/storehistory/'
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message === "success") {
            document.getElementById('cadrstore').innerHTML = `
                <h3>نمایش کارکرد قطعه</h3>
                 <div class="card">
                        <div class="card-body">
                            <div id="addstorecadr" class="timeline">
                  
                                
                                
                                </div>
                                </div>
                `
            document.getElementById('cadrstore').showModal();
            var context = ''
            for (obj in resp.result) {
                // console.log(resp.result[obj].days +" - "+resp.result[obj].starterr+" - "+resp.result[obj].tarikh)
                if (resp.result[obj].starterr === false) {
                    context += ` <div class="timeline-item">
                                    <div>
                                        <a href="#">
                                            <figure class="avatar avatar-sm mr-3 bring-forward">
                                                 <span data-toggle="tooltip" title="` + resp.result[obj].gs + `" class="avatar-title bg-success-bright text-success rounded-circle">` + obj + `</span>
                                            </figure>
                                        </a>
                                    </div>
                                    <div>
                                        <h6 class="d-flex justify-content-between mb-4 primary-font">
                                            <span>
                                            
                                                <a href="#"> کارکرد  </a>` + resp.result[obj].days + ` روز
                                            </span>
 
                                            
                                        </h6>
                                       <div class="mb-3 border p-3 border-radius-1">
                                                 تاریخ نصب ` + resp.result[obj].az + ` | تاریخ معیوبی ` + resp.result[obj].ta + ` 
                                            </div>
                                    </div>
                                </div>
                    `
                } else {
                    context += ` <div class="timeline-item">
                                    <div>
                                        <a href="#">
                                            <figure class="avatar avatar-sm mr-3 bring-forward">
                                                 <span class="avatar-title bg-danger text-dark rounded-circle">` + obj + `</span>
                                            </figure>
                                        </a>
                                    </div>
                                    <div>
                                        <h6 class="d-flex justify-content-between mb-4 primary-font">
                                            <span>                                            
                                                <a href="#"> از ابتدا معیوب
                                            </span>
                                            <span class="text-muted font-weight-normal">` + resp.result[obj].tarikh + `</span>                                            
                                        </h6>                                       
                                    </div>
                                </div>
                    `

                }


            }
            context += `<button class="btn btn-dark" onclick="closecadr()"> 
بستن</button>`
            document.getElementById('addstorecadr').innerHTML = context


            ending()
        }

    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
}

function closecadr() {
    document.getElementById('cadrstore').close();
}

function checkrisk(val) {
    gsid = document.getElementById('GsId').value
    nazel = document.getElementById('NazelId').value
    if (document.getElementById('rpId')) {

        rpId = document.getElementById('rpId').value
    } else {
        rpId = 0
    }
    $.ajax({
        type: 'GET',
        data: {
            'storeid': val,
            'gsid': gsid,
            'nazel': nazel,
            'rpId': rpId,
        },
        dataType: "json",
        url: '/api/get-risk/',
    }).done(function (data) {
        if (data.role === 'tek' && data.otp_peykarbandi !== "1") {
            document.getElementById('peykarbandi').innerHTML = `
            <div class="alert alert-dark" role="alert"><h3> کد پیکربندی: ` + data.otp_peykarbandi + `</h3></div> `
        } else {
            document.getElementById('peykarbandi').innerHTML = ``
        }
        if (data.level == '0') {
            document.getElementById('risket').empty()
        }
        if (data.level == '2') {
            document.getElementById('risket').innerHTML = `
            <div class="alert alert-warning" role="alert">
  این قطعه دارای ریسک متوسط میباشد
   <a href="#" onclick="storehistory(` + data.serial + `)" class="alert-link">(مشاهده سابقه کارکرد قطعه)</a>. در صورتی که جایگاه در راه دور میباشد از قطعه دیگری استفاده کنید.
</div>
            `
        }
        if (data.level == '3') {
            document.getElementById('risket').innerHTML = `
            <div class="alert alert-danger" role="alert">
  این قطعه دارای ریسک بالا میباشد
   <a href="#" onclick="storehistory(\`+data.serial+\`)" class="alert-link">(مشاهده سابقه کارکرد قطعه)</a>. در صورتی که جایگاه در راه دور میباشد از قطعه دیگری استفاده کنید.
</div>
            `
        }

    })
}

function storezonelist(obj, st, nomrator) {
    waiting()

    if (st === 1) {
        document.getElementById('headerid2').innerText = "لیست سریال کارتخوان"
    } else {
        document.getElementById('headerid2').innerText = "لیست سریال صفحه کلید"
    }

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'obj': obj,
            'st': st,
            'nomrator': nomrator,
        },
        url: '/pay/getstorelistzone/',
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

                }
            }
            ending();
        },
        error: function (xhr, status, error) {
            ending(1, error);
        }
    })
}


function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < milliseconds);
}

function getGPS(val) {

    waiting()
    navigator.geolocation.getCurrentPosition(function (position) {

        var lat = position.coords.latitude;
        var lng = position.coords.longitude;
        alarm('info', lat)
        alarm('info', lng)


        sleep(1000);
        $.ajax({
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                'lat': lat.toPrecision(8),
                'long': lng.toPrecision(8),
                'val': val,
            },
            url: '/api/getlatolong/',
            dataType: "json",
            success: function (resp) {

                if (resp.message === "ok") {
                    alarm('info', 'اطلاعات جغرافیایی شما بدرستی بروز رسانی شد . لطفا جهت بررسی مجدد،  گزینه بررسی تیکت را کلیک کنید')
                }
                ending();
            },

            error: function (xhr, status, error) {
                ending(1, error);
            }
        })

    })

}

function sarfaslID() {

    const Sid = document.getElementById('SarfaslId').value;
    waiting();
    let url = '/catFailure/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'Sid': Sid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var obj = 0;
        if (resp.message !== "success") {
            $('#id_failure').empty();
            content += '<option value=0>یک عنوان انتخاب کنید </option>'
            for (obj in resp.mylist) {
                content += '<option value=' + resp.mylist[obj].id + '>' + resp.mylist[obj].info + ' </option>'
            }
            $('#id_failure').append(content);
        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;
}

function Download(item, val) {

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
            ending(1, error);
        });
    return false;

};

function sarfaslIDedit() {

    const Sid = document.getElementById('SarfaslId').value;
    const tid = document.getElementById('ticketId').value
    document.getElementById('peykarbandi').innerHTML = ``
    waiting();
    let url = '/catFailureedit/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'Sid': Sid,
            'tid': tid,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var obj = 0;
        if (resp.message !== "success") {
            $('#id_failure').empty();
            content += '<option value=0>یک عنوان انتخاب کنید </option>'
            for (obj in resp.mylist) {
                content += '<option value=' + resp.mylist[obj].id + '>' + resp.mylist[obj].info + ' </option>'
            }
            $('#id_failure').append(content);

            $('#rpId').empty();
            content = '<option value=0>یک اقدام انتخاب کنید </option>'
            for (obj in resp.myrpid) {
                content += '<option value=' + resp.myrpid[obj].id + '>' + resp.myrpid[obj].info + ' </option>'
            }
            $('#rpId').append(content);
        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;
}

function lock(status, rserial) {
    const meetingnumber = document.getElementById('meeting_number').value;
    if (!meetingnumber) {
        alert('لطفاً شماره صورتجلسه را وارد کنید.');
        return;
    }
    const val = document.getElementById('ticketId').value
    // const pid =document.getElementById('id_position').value
    var serial = 0;
    serial = rserial
    if (status === 1) {
        serial = document.getElementById('id_polomp').value;
    }
    if (status === 2) {
        serial = document.getElementById('id_fak').value
    }
    if (serial.length === 0) {
        alarm('error', 'ابتدا یک سریال انتخاب کنید')
        return false
    }
    if (serial == 0) {
        alarm('error', 'ابتدا یک سریال انتخاب کنید')
        return false
    }
    waiting();
    let url = '/api/addremovelock/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,
            'status': status,
            'serial': serial,
            'meetingnumber': meetingnumber,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var obj = 0;
        if (resp.message != 'success') {
            ending()
            alarm('error', resp.message)
            return false
        }
        $('#id_polomp').empty();
        content += '<option value=0>انتخاب کنید</option>'
        for (obj in resp.polomps) {
            content += '<option value=' + resp.polomps[obj].serial + '>' + resp.polomps[obj].serial + ' </option>'
        }
        $('#id_polomp').append(content);

        var content = '';

        if (resp.status === 1) {

            content += '<tr id="add' + resp.serial + '">';
            content += '<td class="text-primary" id="serial">' + resp.serial + '</td>';

            content += '<td><button class="btn btn-apple" onclick="lock(3, \'' + resp.serial + '\')">واگرد</button></td>';

            content += '</tr>'
            $('#tblList tbody').append(content);
        }
        if (resp.status === 2) {
            if (document.getElementById('id_fak')) {
                document.getElementById('id_fak').value = ''
            }
            content += '<tr id="deleted' + resp.serial + '">';
            content += '<td class="text-primary" id="serial">' + resp.serial + '</td>';

            content += '<td><button class="btn btn-apple" onclick="lock(4, \'' + resp.serial + '\')">واگرد</button></td>';

            content += '</tr>'
            $('#tblList2 tbody').append(content);
        }
        if (resp.status === 3) {
            document.getElementById('add' + resp.serial).remove()
        }
        if (resp.status === 4) {
            document.getElementById('deleted' + resp.serial).remove()
        }

        ending();
        alarm('info', 'عملیات با موفقیت انجام شد')
    })
        .fail(function (xhr, status, error) {
            ending(1, error);

        });
    return false;

}

function runlock(val, rnd) {

    waiting();
    document.getElementById('ticketId').value = val
    let url = '/api/runremovelock/';

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,
            'rnd': rnd,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var obj = 0;
        // var content = '';
        // $('#id_position').empty();
        // for (obj in resp.position) {
        //     content += '<option value=' + resp.position[obj].id + '>' + resp.position[obj].name + ' </option>'
        // }
        // $('#id_position').append(content);
        document.getElementById('meeting_number').value = resp.meetingnumber
        var content = '';

        content += '<option value=0>انتخاب کنید</option>'

        $('#id_polomp').empty();
        for (obj in resp.polomps) {
            content += '<option value=' + resp.polomps[obj].serial + '>' + resp.polomps[obj].serial + ' </option>'
        }
        $('#id_polomp').append(content);


        $('#tblList tbody').empty()
        $('#tblList2 tbody').empty()
        if (document.getElementById('id_fak')) {
            document.getElementById('id_fak').value = ''
        }
        for (obj in resp.installlock) {

            content = '';
            content += '<tr id="add' + resp.installlock[obj].serial + '">';
            content += '<td class="text-primary" id="serial">' + resp.installlock[obj].serial + '</td>';
            if (resp.istek) {
                content += '<td><button class="btn btn-apple" onclick="lock(3, \'' + resp.installlock[obj].serial + '\')">واگرد</button></td>';
            }
            content += '</tr>'
            $('#tblList tbody').append(content);
        }
        for (obj in resp.removelock) {
            content = '';
            content += '<tr id="deleted' + resp.removelock[obj].serial + '">';
            content += '<td class="text-primary" id="serial">' + resp.removelock[obj].serial + '</td>';
            if (resp.istek) {
                content += '<td><button class="btn btn-apple" onclick="lock(4, \'' + resp.removelock[obj].serial + '\')">واگرد</button></td>';
            }
            content += '</tr>'
            $('#tblList2 tbody').append(content);
        }

        document.getElementById('lockgs_id').innerText = 'جایگاه: ' + resp.gsname + '  شماره نازل : ' + resp.gspump;

        ending();

    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;

}


function runerjatotek(val) {
    document.getElementById('ticketId').value = val
    waiting();

    let url = '/api/runerjatotek/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var obj = 0;
        $('#id_erjatotek').empty();

        for (obj in resp.teks) {
            content += '<option value=' + resp.teks[obj].id + '>' + resp.teks[obj].name + '  </option>'
        }
        $('#id_erjatotek').append(content);


        ending();

    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;

}

function erjatotek() {
    const val = document.getElementById('ticketId').value
    const user = document.getElementById('id_erjatotek').value
    waiting();

    let url = '/api/ErjaToTek/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,
            'user': user,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        alarm('info', 'عملیات با موفقیت انجام شد')

        ending();

    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;

}

function GETModemList(gid, st) {
    waiting();

    let url = '/api/getmodemlist/';

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'gid': gid,
            'st': st,

        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        $('#tblmodel tbody').empty()
        var content = '';
        for (obj in resp.mylist) {
            content += '<tr id="add' + resp.mylist[obj].id + '">';
            content += '<td class="text-primary" id="serial">' + resp.mylist[obj].id + '</td>';
            content += '<td class="text-primary" id="serial">' + resp.mylist[obj].in + '</td>';
            content += '<td class="text-primary" id="serial">' + resp.mylist[obj].out + '</td>';


            content += '</tr>'
        }
        $('#tblmodel tbody').append(content);
        ending();

    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;
}


function runstore(val, rnd) {

    waiting();
    document.getElementById('ticketId').value = val
    let url = '/api/runstore/';

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,
            'rnd': rnd,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var obj = 0;

        var content = '';

        content += '<option value=0>انتخاب کنید</option>'

        $('#id_store').empty();

        for (obj in resp.polomps) {
            content += '<option value=' + resp.polomps[obj].serial+'>'+resp.polomps[obj].serial + ' - ' +resp.polomps[obj].status +'</option>'
        }
        $('#id_store').append(content);


        $('#tblList tbody').empty()

        if (document.getElementById('id_fak')) {
            document.getElementById('id_fak').value = ''
        }
        for (obj in resp.installlock) {

            content = '';
            content += '<tr id="add' + resp.installlock[obj].serial + '">';
            content += '<td class="text-primary" id="serial">' + resp.installlock[obj].serial + ' - ' +resp.installlock[obj].status+'</td>';
            if (resp.istek) {
                content += '<td><button class="btn btn-apple" onclick="assinstore(2, \'' + resp.installlock[obj].serial + '\')">واگرد</button></td>';
            }
            content += '</tr>'
            $('#tblList tbody').append(content);
        }


        document.getElementById('lockgs_id').innerText = 'جایگاه: ' + resp.gsname + '  شماره نازل : ' + resp.gspump;

        ending();

    })
        .fail(function (xhr, status, error) {
            ending(1, error);
        });
    return false;

}

function assinstore(status, rserial) {

    const val = document.getElementById('ticketId').value
    // const pid =document.getElementById('id_position').value
    var serial = 0;

        serial = rserial
    if (status === 1) {
        serial = document.getElementById('id_store').value;
    }

    if (serial.length === 0) {
        alarm('error', 'ابتدا یک سریال انتخاب کنید')
        return false
    }
    if (serial == 0) {
        alarm('error', 'ابتدا یک سریال انتخاب کنید')
        return false
    }
    waiting();
    let url = '/api/AssignStore/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'val': val,
            'serial': serial,
            'status':status,


        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        var obj = 0;
        if (resp.message != 'success') {
            ending()
            alarm('error', resp.message)
            return false
        }
        $('#id_store').empty();
        content += '<option value=0>انتخاب کنید</option>'
        for (obj in resp.polomps) {
            content += '<option value=' + resp.polomps[obj].serial + '>' + resp.polomps[obj].serial + ' - ' +resp.polomps[obj].status+' </option>'
        }
        $('#id_store').append(content);

        var content = '';

        if (resp.status === 1) {

            content += '<tr id="add' + resp.serial + '">';
            content += '<td class="text-primary" id="serial">' + resp.serial + ' - ' +resp.st+'</td>';

            content += '<td><button class="btn btn-apple" onclick="assinstore(2, \'' + resp.serial + '\')">واگرد</button></td>';

            content += '</tr>'
            $('#tblList tbody').append(content);
        }
     if (resp.status === 2) {

            document.getElementById('add' + resp.serial).remove()
            document.getElementById('add' + resp.serial).remove()
        }

        ending();
        alarm('info', 'عملیات با موفقیت انجام شد')
    })
        .fail(function (xhr, status, error) {
            ending(1, error);

        });
    return false;

}