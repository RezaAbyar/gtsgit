function InsertPan(val) {
    waiting();

    let pan = document.getElementById('pan').value;
    let tarikh = document.getElementById('select').value;
    let id_gs = document.getElementById('id_gs').value;
    let insPlk_FirstCode = document.getElementById('insPlk_FirstCode').value;
    let insPlk_SecondCode = document.getElementById('insPlk_SecondCode').value;
    let insPlk_CityCode = document.getElementById('insPlk_CityCode').value;
    let insPlk_CharCode = document.getElementById('insPlk_CharCode').value;
    let insPlk_FirstCode_MS = document.getElementById('insPlk_FirstCode_MS').value;
    let insPlk_SecondCode_MS = document.getElementById('insPlk_SecondCode_MS').value;
    let idstatus = document.getElementById('idstatus').value;
    var tdate = document.getElementById('datecheck').value

    if (tdate < tarikh) {
        alarm('danger', 'تاریخ انتخاب شده از تاریخ روز جاری بیشتر است');
        ending();
        return false;

    }


    if (tarikh.length !== 10) {
        alarm('danger', 'تاریخ نا معتبر است');
        ending();
        return false;

    }
    var regEx = /^(\d{4})(\/|-)(\d{2})(\/|-)(\d{2})$/;
    if (!tarikh.match(regEx)) {
        alarm('danger', 'تاریخ نا معتبر است');
        ending();
        return false;
    }  // Invalid format
    if (id_gs.length === 0) {
        alarm('danger', 'نام جایگاه را انتخاب کنید');
        ending();
        return false;
    }
    if (val.length === 16) {
        $.ajax({
            type: 'POST', data: {
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                'pan': pan,
                'tarikh': tarikh,
                'id_gs': id_gs,
                'insPlk_FirstCode': insPlk_FirstCode,
                'insPlk_SecondCode': insPlk_SecondCode,
                'insPlk_CityCode': insPlk_CityCode,
                'insPlk_CharCode': insPlk_CharCode,
                'insPlk_FirstCode_MS': insPlk_FirstCode_MS,
                'insPlk_SecondCode_MS': insPlk_SecondCode_MS,
                'idstatus': idstatus,
            }, url: "/cart/addpan/",
        }).done(function (data) {
            if (data.message === 'warning') {
                alarm('danger', 'شماره پن اشتباه ثبت شده است');
                alarm('warning', 'لطفا در خواندن اعداد دقت کنید');
            }
            if (data.message === 'error') {
                alarm('warning', data.info);
            }
            if (data.message === 'success') {
                alarm('success', 'با موفقیت ثبت شد');

                $(".response").html('11');
                $(".response").show();
                document.getElementById('pan').value = "7744330";
                document.getElementById('insPlk_FirstCode').value = "";
                document.getElementById('insPlk_SecondCode').value = "";
                document.getElementById('insPlk_CityCode').value = "";
                document.getElementById('insPlk_CharCode').value = "";
                document.getElementById('insPlk_FirstCode_MS').value = "";
                document.getElementById('insPlk_SecondCode_MS').value = "";

                document.getElementById('insPlk_FirstCode').focus();
            }
            ending();
        })
            .fail(function (xhr, status, error) {
                ending(1,error);
            });

    } else {
        ending();
        alarm('danger', 'عملیات شکست خورد شماره پن باید 16 رقم باشد');

    }

}


function InsertPost(val) {


    waiting();

    let pan = document.getElementById('pan').value;
    let tarikh = document.getElementById('select').value;


    let idstatus = document.getElementById('idstatus').value;
    if (tarikh.length !== 10) {
        alarm('danger', 'تاریخ نا معتبر است');
        return false;
    }
    var regEx = /^(\d{4})(\/|-)(\d{2})(\/|-)(\d{2})$/;
    if (!tarikh.match(regEx)) {
        alarm('danger', 'تاریخ نا معتبر است');
        return false;
    }  // Invalid format

    if (val.length === 16) {
        $.ajax({
            type: 'POST', data: {
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                'pan': pan,
                'tarikh': tarikh,

                'idstatus': idstatus,
            }, url: "/cart/addPanpost/",
        }).done(function (data) {
            if (data.message === 'warning') {
                alarm('danger', 'شماره پن اشتباه ثبت شده است');
                alarm('warning', 'لطفا در خواندن اعداد دقت کنید');
            }
            if (data.message === 'error') {
                alarm('warning', 'شماره کارت تکراری است');
            }
            if (data.message === 'success') {
                alarm('success', 'با موفقیت ثبت شد');

                $(".response").html('11');
                $(".response").show();
                document.getElementById('pan').value = "7744330";

            }
            ending();
        })
            .fail(function (xhr, status, error) {
                ending(1,error);
            });
    } else {
        alarm('danger', 'عملیات شکست خورد شماره پن باید 16 رقم باشد');
        ending();
    }

}

function getArea(gscode) {
    waiting();

    if (gscode === '0') {
        gscode = document.getElementById('id_zone').value;
    }
    let url = '/cart/AreaZone/';
    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value, 'myTag': gscode,
        }, dataType: "json", url: url,
    }).done(function (data) {
        var content = '';
        $('#id_area').empty();
        content += '<option value=0>یک ناحیه انتخاب کنید</option>';
        for (obj in data.mylist) {
            const mlist = data.mylist[obj];

            content += '<option value=' + mlist.id + '>' + mlist.name + '</option>';


        }
        $('#id_area').append(content);
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1,error);
        });
}


function getGS(areacode) {

    waiting()

    if (areacode === '0') {
        areacode = document.getElementById('id_area').value;
    }
    let url = '/cart/AreaGS/';
    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value, 'myTag': areacode,
        }, dataType: "json", url: url,
    }).done(function (data) {
        var content = '';

        $('#id_gs').empty();
        content += '<option value=0>یک جایگاه انتخاب کنید</option>';
        for (obj in data.mylist) {
            const mlist = data.mylist[obj];
            content += '<option value=' + mlist.id + '>' + mlist.name + '</option>';
        }
        $('#id_gs').append(content);
        ending();
    });
}

function ToMalek() {
    waiting();
    var idsArr2 = [];
    $('.checkbox:checked').each(function () {
        idsArr2.push($(this).attr('data-id'));
    });

    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا یک آیتم را انتخاب کنید');
    } else if (idsArr2.length > 1) {
        alarm('warning', 'لطفا فقط یک آیتم را انتخاب کنید');
    } else {

        document.getElementById('malekId').value = idsArr2;
        bypass = document.getElementById('bypassid').value;
        $('#AddToMalek').modal('show');
        $('#otpbox').empty();
        $('#btnotp').empty();

        if (bypass === 'True') {
            $('#btnotp').append(`
                       <ul class="nav">
                                      <li  class="nav-item">
                           
                            <button style="color: #fffbff; display: none" id="SaveMalekId"
                                    class="btn btn-primary"
                                    title="کد احراز هویت"
                                    data-dismiss="modal"
                                    data-toggle="tooltip" onclick="SaveToMalekbypass()">
                                <i data-feather="plus" aria-hidden="true"></i>تحویل به مالک
                            </button>
                            
                        </li>



                    </ul>
        

           `);
        } else {
            $('#btnotp').append(`
                       <ul class="nav">
                                      <li  class="nav-item">
                           
                            <button style="color: #fffbff; display: none" id="SaveMalekId"
                                    class="btn btn-primary"
                                    title="کد احراز هویت"
                                    data-toggle="tooltip" onclick="sendotptomalek(document.getElementById('mobailmalek').value,document.getElementById('codemelimalek').value)">
                                <i data-feather="plus" aria-hidden="true"></i>درخواست کد احراز هویت
                            </button>
                            
                        </li>



                    </ul>
        

           `);
        }

    }
    ending();
}

function SaveToMalek() {
    waiting();

    var codemelimalek = document.getElementById("codemelimalek").value;
    var name = document.getElementById("otp_id").value;
    var mobail = document.getElementById("mobailmalek").value;
    if (name === '') {
        alarm('warning', 'لطفا کد احراز هویت را وارد کنید');
    } else if (mobail === '') {
        alarm('warning', 'لطفا  شماره تماس مالک را وارد کنید');

    } else if (codemelimalek === '') {
        alarm('warning', 'لطفا کد ملی مالک را وارد کنید');

    } else {
        if (confirm('برای انتقال کارت به مالک مطمئن هستید؟')) {
            var strIds2 = document.getElementById('malekId').value;
            codemelimalek = document.getElementById('codemelimalek').value;
            showcardmeli = document.getElementById('showcardmeli').value;
            showcardcar = document.getElementById('showcardcar').value;
            namemalek = document.getElementById('namemalek').value;
            mobailmalek = document.getElementById('mobailmalek').value;

            $.ajax({
                url: "/cart/carttomalek/", type: 'post', data: {
                    'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                    'strIds': strIds2,
                    'codemelimalek': codemelimalek,
                    'showcardmeli': showcardmeli,
                    'showcardcar': showcardcar,
                    'namemalek': namemalek,
                    'mobailmalek': mobailmalek,
                    'otp': name,
                }
            }).done(function (resp) {
                if (resp.message === "success") {
                    $('.checkbox:checked').each(function () {
                        $(this).parents("tr").remove();
                    });

                    alarm('success', 'کارت سوخت بدرستی به مالک منتقل شد');
                    ending();
                } else {
                    alarm('error', 'کد وارد شده اشتباست');
                    ending();
                }

            })
                .fail(function (resp, jqXHR, textStatus, errorThrown) {
                    ending(1,error);
                });
        }
    }
}

function SaveToMalekbypass() {
    waiting();

    var codemelimalek = document.getElementById("codemelimalek").value;

    var mobail = document.getElementById("mobailmalek").value;
    if (mobail === '') {
        alarm('warning', 'لطفا  شماره تماس مالک را وارد کنید');

    } else if (codemelimalek === '') {
        alarm('warning', 'لطفا کد ملی مالک را وارد کنید');

    } else {
        if (confirm('برای انتقال کارت به مالک مطمئن هستید؟')) {
            var strIds2 = document.getElementById('malekId').value;
            codemelimalek = document.getElementById('codemelimalek').value;
            showcardmeli = document.getElementById('showcardmeli').value;
            showcardcar = document.getElementById('showcardcar').value;
            namemalek = document.getElementById('namemalek').value;
            mobailmalek = document.getElementById('mobailmalek').value;

            $.ajax({
                url: "/cart/carttomalek/", type: 'post', data: {
                    'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                    'strIds': strIds2,
                    'codemelimalek': codemelimalek,
                    'showcardmeli': showcardmeli,
                    'showcardcar': showcardcar,
                    'namemalek': namemalek,
                    'mobailmalek': mobailmalek,
                    'otp': '1111',
                }
            }).done(function (resp) {
                if (resp.message === "success") {
                    $('.checkbox:checked').each(function () {
                        $(this).parents("tr").remove();
                    });

                    alarm('success', 'کارت سوخت بدرستی به مالک منتقل شد');
                    ending();
                } else {
                    alarm('error', 'کد وارد شده اشتباست');
                    ending();
                }

            })
                .fail(function (resp, jqXHR, textStatus, errorThrown) {
                    ending(1,error);
                });
        }
    }
}


function SaveToArea() {
    waiting();
    var idsArr = [];
    $('.checkbox:checked').each(function () {
        idsArr.push($(this).attr('data-id'));
    });
    if (idsArr.length < 1) {
        alert('لطفا یک آیتم را انتخاب کنید');
        ending()
    } else {
        if (confirm('برای انتقال کارت ها به ناحیه مطمئن هستید؟')) {
            var strIds = idsArr.join(",");

            $.ajax({
                url: "/cart/carttonahye/",
                type: 'post',
                data: {
                    'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                    'strIds': strIds,
                }
            }).done(function (resp) {
                $('.checkbox:checked').each(function () {
                    $(this).parents("tr").remove();
                });
                alarm('success', 'کارت سوخت (ها) بدرستی به ناحیه منتقل شد');
                ending();

            })
                .fail(function (xhr, status, error) {
                    ending(1,error);
                });


        } else {
            ending()
        }
    }
}


function SaveToZone() {
    waiting();

    var idsArr = [];
    $('.checkbox:checked').each(function () {
        idsArr.push($(this).attr('data-id'));
    });
    if (idsArr.length < 1) {
        alert('لطفا یک آیتم را انتخاب کنید');
        ending()
    } else {
        if (confirm('برای انتقال کارت ها به منطقه مطمئن هستید؟')) {
            var strIds = idsArr.join(",");

            $.ajax({
                url: "/cart/carttozone/",
                type: 'post',
                data: {
                    'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                    'strIds': strIds
                }

            }).done(function (resp) {
                $('.checkbox:checked').each(function () {
                    $(this).parents("tr").remove();
                });
                alarm('success', 'کارت سوخت (ها) بدرستی به منطقه منتقل شد');
                ending();

            })
                .fail(function (xhr, status, error) {
                    ending(1,error);
                });
        } else {
            ending()
        }


    }

}


function SaveToEmha() {
    waiting();

    var idsArr = [];
    $('.checkbox:checked').each(function () {
        idsArr.push($(this).attr('data-id'));
    });
    if (idsArr.length < 1) {
        alert('لطفا یک آیتم را انتخاب کنید');
        ending()
    } else {
        if (confirm('برای امحا کارت ها  مطمئن هستید؟')) {
            var strIds = idsArr.join(",");

            $.ajax({
                url: "/cart/carttoemha/", type: 'post', data: {
                    'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                    'strIds': strIds
                }
            }).done(function (resp) {
                $('.checkbox:checked').each(function () {
                    $(this).parents("tr").remove();
                });
                alarm('success', 'کارت سوخت (ها) بدرستی امحا شد');
                ending();

            })

                .fail(function (xhr, status, error) {
                    ending(1,error);
                });
        } else {
            ending()
        }
    }
}

function getWorkflowCard(obj) {
    waiting();


    let url = '/cart/getWorkflowCard/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'obj': obj,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message !== "success") {


            $('#ListCardId').empty();
            content += '<div class="timeline">';
            for (obj in resp.mylist) {
                content += '<div class="timeline-item"><div class="timeline-item"><div><figure class="avatar avatar-sm mr-3 bring-forward"><span class="avatar-title bg-success-bright text-success rounded-circle">' + resp.mylist[obj].count + '</span></figure></div>';

                content += '<div><h6 class="d-flex justify-content-between mb-4 primary-font">';

                if (obj === '0') {
                    content += '<a href="#">' + resp.mylist[obj].user + '</a> ثبت اولیه</span>';
                } else {
                    content += '<a href="#">' + resp.mylist[obj].user + '</a>' + resp.mylist[obj].info + '</span>';
                }
                content += '<span class="text-muted font-weight-normal">' + resp.mylist[obj].date + '</span></h6>';
                if (resp.mylist[obj].name.length > 0) {
                    content += '<a href="#"><div class="mb-3 border p-3 border-radius-1"> ' + resp.mylist[obj].name + '</div> </a>';
                }
                content += '</div> </div> </div>';
            }

            $('#ListCardId').append(content);
            ending();
        }

    })
        .fail(function (xhr, status, error) {
            ending(1,error);
        });
    return false;
}

function getWorkflowCardAzad(obj) {
    waiting();


    let url = '/cart/getWorkflowCardAzad/';
    var content = '';
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'obj': obj,
        },
        url: url,
        dataType: "json",
    }).done(function (resp) {
        if (resp.message !== "success") {


            $('#ListCardId').empty();
            content += '<div class="timeline">';
            for (obj in resp.mylist) {
                content = '';
                content += '<div class="timeline-item"><div><figure class="avatar avatar-sm mr-3 bring-forward"><span class="avatar-title bg-success-bright text-success rounded-circle">' + resp.mylist[obj].count + '</span></figure></div>';

                content += '<div><h6 class="d-flex justify-content-between mb-4 primary-font">';
                content += '<a href="#">' + resp.mylist[obj].user + '</a>' + resp.mylist[obj].info + '</span>';
                content += '<span class="text-muted font-weight-normal">' + resp.mylist[obj].date + '</span></h6>';
                content += '</div><hr/>';
                $('#ListCardId').append(content);
                ending();
            }
        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1,error);
        });
    return false;
}

function paneditItem(val) {
 document.getElementById('oldpanid').value =val

    $.ajax({
        cache: false,
        url: "/api/get-pan-edit",
        data: {
            val: val,
        },
        success: function (data) {


                document.getElementById('item_info2').value = data.val;


        },
        error: function (xhr, status, error) {


        }
    });
}

function panupdateItem(id) {
    var val = document.getElementById('oldpanid').value;

    var newval;
        newval = document.getElementById('item_info2').value;



    $.ajax({
        cache: false,
        url: "/api/set-pan-edit",
        data: {
            val: val,
            newval: newval,
        },
        success: function (data) {


                document.getElementById('panid').innerText = data.newname;



            alarm('success', 'اطلاعات جایگاه بروزرسانی شد');

        },
        error: function (xhr, status, error) {


        }
    });
}

function sendotptomalek(mobail, codemeli) {
    waiting();

    let url = '/api/send-otp-to-malek/';
    $.ajax({
        type: 'GET', data: {
            'mobail': mobail, 'codemeli': codemeli,
        }, dataType: "json", url: url,
    }).done(function (data) {
        if (data.message === "sendotp") {
            var content = '';
            content = `
 <div class="form-group">
                                    <label  for="otp_id">کد احراز هویت
                                    <input maxlength="5" type="text" class="form-control" id="otp_id">
                                        </label>   
                                    
                 <button  id="SaveMalekId"
                                    class="btn btn-info"
                                    title="ذخیره اطلاعات مالک"
                                    data-toggle="tooltip" onclick="SaveToMalek()">
                                <i data-feather="plus" aria-hidden="true"></i>تایید و ذخیره
                            </button>
                          </div> 
`
            $('#otpbox').append(content);
            $('#btnotp').empty();


        }
        ending();
    })
        .fail(function (xhr, status, error) {
            ending(1,error);
        });
}
