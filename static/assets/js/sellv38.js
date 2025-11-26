function addnazel() {
    waiting()

    var end = document.getElementById('id_end').value
    var start = document.getElementById('id_start').value
    if (document.getElementById('id_start2')) {
        var start2 = document.getElementById('id_start2').value
        var end2 = document.getElementById('id_end2').value
    }
    var sell = document.getElementById('id_sell').value
    var sellshow = document.getElementById('id_sell_show').value
    var yarane = document.getElementById('id_yarane').value
    var nimeyarane = document.getElementById('id_nimeyarane').value
    var azad = document.getElementById('id_azad').value
    var ezterari = document.getElementById('id_ezterari').value
    var sellkol = document.getElementById('id_sellkol_show').value
    var gsid = document.getElementById('id_mygsid').value
    var id_ekhtelaf = document.getElementById('id_ekhtelaf').value
    var mojaz = document.getElementById('id_mojaz').value
    var nomojaz = document.getElementById('id_nomojaz').value
    var azmayesh = document.getElementById('id_azmayesh').value
    var havale = document.getElementById('id_havale').value
    var tarikh = document.getElementById('select').value
    var number = document.getElementById('id_num_show').value
    // var id_benzin_mojodi = document.getElementById('id_benzin_mojodi').value
    // var id_super_mojodi = document.getElementById('id_super_mojodi').value
    // var id_gaz_mojodi = document.getElementById('id_gaz_mojodi').value

    // const file = fileInput.files[0];

    // const formData = new FormData();
    // formData.append('image', file);
    // if (!file) {
    //     alert('لطفاً یک عکس انتخاب کنید.');
    //     return;
    // }
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'end': end,
            'end2': end2,
            'start': start,
            'start2': start2,
            'sellshow': sellshow,
            'yarane': yarane,
            'nimeyarane': nimeyarane,
            'azad': azad,
            'ezterari': ezterari,
            'sellkol': sellkol,
            'id_ekhtelaf': id_ekhtelaf,
            'mojaz': mojaz,
            'nomojaz': nomojaz,
            'azmayesh': azmayesh,
            'havale': havale,
            'tarikh': tarikh,
            'number': number,
            'gsid': gsid,

        },
        url: '/api/addnazel/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {
                alarm('success', 'با موفقیت ثبت شد')
                clearSell()
                $('#id_num_show option:selected').removeAttr('selected')
                    .next('option').attr('selected', 'selected');
                var newid = document.getElementById('id_num_show').value
                showNazelId(newid)
            } else {
                alarm('error', resp.message)
                ending()
                return false
            }
            $('#tableSell tbody').empty()
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                var content = '';
                content += '<tr id=' + mlist.tolombeinfo + '>'

                content += '<td class="text-center">' + mlist.pumpnumber + '</td>'
                content += '<td class="text-center">' + mlist.end + '</td>'
                content += '<td class="text-center">' + mlist.start + '</td>'
                content += '<td class="text-center">' + mlist.sell + '</td>'
                content += '<td class="text-center">' + mlist.sellkol + '</td>'
                content += '<td class="text-center">' + mlist.ekhtelaf + '</td>'
                content += '<td class="text-center">' + mlist.mojaz + '</td>'
                if (mlist.nomojaz === '0.00') {
                    content += '<td class="text-center">' + mlist.nomojaz + '</td>'
                } else {
                    content += '<td style="background: tomato; color: #0b0b0b" class="text-center">' + mlist.nomojaz + '</td>'
                }
                $('#tableSell tbody').append(content);

            }
            const summlist = resp.sumlist[0]

            document.getElementById('id_summek').value = summlist.summek
            document.getElementById('id_sumelk').value = summlist.sumelk
            ending()
        },
        error: function (xhr, status, error) {
            clearSell()
            ending(1, error);
        }
    })
}

function showNazelId(val) {

    waiting()
    clearSell()
    if (val === 0) {

    }
    var gsid = document.getElementById('id_mygsid').value
    var tarikh = document.getElementById('select').value
    var val = document.getElementById('id_num_show').value
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'val': val,
            'gsid': gsid,
            'tarikh': tarikh,
        },
        url: '/sell/nazelrow/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {

                const tlist1 = resp.tlist[0]

                document.getElementById('id_benzin_mojodi').value = tlist1.benzin
                document.getElementById('id_super_mojodi').value = tlist1.super
                document.getElementById('id_gaz_mojodi').value = tlist1.gaz
                const mlist = resp.mylist[0]
                document.getElementById('id_start').value = mlist.start
                document.getElementById('id_end').value = mlist.end
                if (document.getElementById('id_start2')) {
                    document.getElementById('id_start2').value = mlist.start2
                    document.getElementById('id_end2').value = mlist.end2
                }
                document.getElementById('id_end').readOnly = true
                document.getElementById('id_end').disabled = true
                if (mlist.locked) {
                    document.getElementById('id_start').readOnly = true
                    document.getElementById('id_start').disabled = true
                    document.getElementById('id_end').readOnly = true
                    document.getElementById('id_end').disabled = true
                } else {
                    document.getElementById('id_start').removeAttribute('readonly')
                    document.getElementById('id_start').removeAttribute('disabled')

                }
                if (resp.isedit === 1) {

                    document.getElementById('id_start').removeAttribute('readonly')
                    document.getElementById('id_start').removeAttribute('disabled')
                    document.getElementById('id_end').removeAttribute('readonly')
                    document.getElementById('id_end').removeAttribute('disabled')

                    document.getElementById('id_azad').removeAttribute('readonly')
                    document.getElementById('id_azad').removeAttribute('disabled')
                    document.getElementById('id_yarane').removeAttribute('readonly')
                    document.getElementById('id_yarane').removeAttribute('disabled')
                    document.getElementById('id_nimeyarane').removeAttribute('readonly')
                    document.getElementById('id_nimeyarane').removeAttribute('disabled')

                    document.getElementById('id_ezterari').removeAttribute('readonly')
                    document.getElementById('id_ezterari').removeAttribute('disabled')

                    document.getElementById('id_azmayesh').removeAttribute('readonly')
                    document.getElementById('id_azmayesh').removeAttribute('disabled')

                    document.getElementById('id_havale').removeAttribute('readonly')
                    document.getElementById('id_havale').removeAttribute('disabled')
                } else {

                    document.getElementById('id_azad').readOnly = true
                    document.getElementById('id_azad').disabled = true
                    document.getElementById('id_yarane').readOnly = true
                    document.getElementById('id_yarane').disabled = true
                    document.getElementById('id_nimeyarane').readOnly = true
                    document.getElementById('id_nimeyarane').disabled = true

                    document.getElementById('id_ezterari').readOnly = true
                    document.getElementById('id_ezterari').disabled = true
                    document.getElementById('id_azmayesh').readOnly = true
                    document.getElementById('id_azmayesh').disabled = true

                    document.getElementById('id_havale').readOnly = true
                    document.getElementById('id_havale').disabled = true


                }
                if (mlist.pumpname === 's') {
                    document.getElementById('id_yarane').value = '0'
                    document.getElementById('id_nimeyarane').value = '0'
                    document.getElementById('id_yarane').readOnly = true;
                    document.getElementById('id_nimeyarane').readOnly = true;
                    document.getElementById('id_azad').readOnly = true;
                    document.getElementById('id_azad').value = '0'
                    document.getElementById('id_ezterari').value = mlist.ezterari
                }
                if (mlist.pumpname === 'b') {
                    document.getElementById('nameyar').innerHTML = ' یارانه ایی'
                    document.getElementById('id_yarane').readOnly = false;
                    document.getElementById('id_nimeyarane').readOnly = false;
                    document.getElementById('id_azad').readOnly = false;
                    document.getElementById('id_yarane').value = mlist.yarane
                    document.getElementById('id_nimeyarane').value = mlist.nimeyarane
                    document.getElementById('id_azad').value = mlist.azad
                    document.getElementById('id_ezterari').value = mlist.ezterari
                }
                if (mlist.pumpname === 'm') {
                    document.getElementById('nameyar').innerHTML = ' یارانه ایی'
                    document.getElementById('id_yarane').readOnly = false;
                    document.getElementById('id_nimeyarane').readOnly = false;
                    document.getElementById('id_azad').readOnly = false;
                    document.getElementById('id_yarane').value = mlist.yarane
                    document.getElementById('id_nimeyarane').value = mlist.nimeyarane
                    document.getElementById('id_azad').value = mlist.azad
                    document.getElementById('id_ezterari').value = mlist.ezterari
                }

                if (mlist.pumpname === 'g') {
                    document.getElementById('id_yarane').value = mlist.yarane
                    document.getElementById('id_nimeyarane').value = mlist.nimeyarane


                    document.getElementById('id_yarane').readOnly = false;
                    document.getElementById('id_azad').readOnly = false;

                    document.getElementById('id_ezterari').value = mlist.ezterari
                    document.getElementById('id_azad').value = mlist.azad
                }
                document.getElementById('id_ezterari').value = mlist.ezterari
                document.getElementById('id_azmayesh').value = mlist.azmayesh
                document.getElementById('id_havale').value = mlist.havaleh
                document.getElementById('id_sell_show').value = mlist.sell
                document.getElementById('id_sellkol_show').value = mlist.sellkol
                document.getElementById('id_ekhtelaf').value = mlist.ekhtelaf
                document.getElementById('id_mojaz').value = mlist.mojaz
                document.getElementById('id_nomojaz').value = mlist.nomojaz
                if (resp.is_close_sell === 'open') {
                    document.getElementById('closebtnid').style.display = 'block'
                    document.getElementById('id_start2').readOnly = false;
                    document.getElementById('id_end2').readOnly = false;
                    document.getElementById('closetitelid').style.display = 'none'
                } else {
                    document.getElementById('closetitelid').style.display = 'block'
                    document.getElementById('closebtnid').style.display = 'none'
                    document.getElementById('id_start2').readOnly = true;
                    document.getElementById('id_end2').readOnly = true;
                }

            }
            ending()

        },
        error: function (xhr, status, error) {
            clearSell()
            ending(1, error);
        }
    })
}

function addnazel2() {
    waiting()
    var end = document.getElementById('id_end').value
    var start = document.getElementById('id_start').value
    var sell = document.getElementById('id_sell').value
    var sellshow = document.getElementById('id_sell_show').value
    var yarane = document.getElementById('id_yarane').value
    var nimeyarane = document.getElementById('id_nimeyarane').value
    var azad = document.getElementById('id_azad').value
    var ezterari = document.getElementById('id_ezterari').value
    var sellkol = document.getElementById('id_sellkol_show').value
    var gsid = document.getElementById('gs_id').value
    var id_ekhtelaf = document.getElementById('id_ekhtelaf').value
    var mojaz = document.getElementById('id_mojaz').value
    var nomojaz = document.getElementById('id_nomojaz').value
    var azmayesh = document.getElementById('id_azmayesh').value
    var havale = document.getElementById('id_havale').value
    var tarikh = document.getElementById('select').value
    var tarikh2 = document.getElementById('select2').value
    var number = document.getElementById('id_num_show').value
    var tarikh3 = document.getElementById('select3').value
    var information = document.getElementById('information').value


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'end': end,
            'start': start,
            'sellshow': sellshow,
            'yarane': yarane,
            'nimeyarane': nimeyarane,
            'azad': azad,
            'ezterari': ezterari,
            'sellkol': sellkol,
            'id_ekhtelaf': id_ekhtelaf,
            'mojaz': mojaz,
            'nomojaz': nomojaz,
            'azmayesh': azmayesh,
            'havale': havale,
            'tarikh': tarikh,
            'tarikh2': tarikh2,
            'number': number,
            'gsid': gsid,
            'tarikh3': tarikh3,
            'information': information,

        },
        url: '/api/addnazel2/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {
                alarm('success', 'با موفقیت ثبت شد')
                clearSell()
                $('#id_num_show option:selected').removeAttr('selected')
                    .next('option').attr('selected', 'selected');
                var newid = document.getElementById('id_num_show').value
                showNazelId2(newid)
            } else {
                alarm('error', resp.message)
                ending()
                return false
            }
            $('#tableSell tbody').empty()
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                var content = '';
                content += '<tr id=' + mlist.tolombeinfo + '>'

                content += '<td class="text-center">' + mlist.pumpnumber + '</td>'
                content += '<td class="text-center">' + mlist.end + '</td>'
                content += '<td class="text-center">' + mlist.start + '</td>'
                content += '<td class="text-center">' + mlist.sell + '</td>'
                content += '<td class="text-center">' + mlist.sellkol + '</td>'
                content += '<td class="text-center">' + mlist.ekhtelaf + '</td>'
                content += '<td class="text-center">' + mlist.mojaz + '</td>'
                if (mlist.nomojaz === '0.00') {
                    content += '<td class="text-center">' + mlist.nomojaz + '</td>'
                } else {
                    content += '<td style="background: tomato; color: #0b0b0b" class="text-center">' + mlist.nomojaz + '</td>'
                }
                $('#tableSell tbody').append(content);

            }
            const summlist = resp.sumlist[0]

            document.getElementById('id_summek').value = summlist.summek
            document.getElementById('id_sumelk').value = summlist.sumelk
            ending()
        },
        error: function () {
            ending(1, error);
        }

    })
}

function showNazelId2(val) {
    waiting()
    clearSell()
    if (val === 0) {

    }
    var gsid = document.getElementById('gs_id').value
    var tarikh = document.getElementById('select').value
    var tarikh2 = document.getElementById('select2').value
    var val = document.getElementById('id_num_show').value
    var tarikh3 = document.getElementById('select3').value
    var qrtime = document.getElementById('qrtime_id').value

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'val': val,
            'gsid': gsid,
            'tarikh': tarikh,
            'tarikh2': tarikh2,
            'tarikh3': tarikh3,
            'qrtime': qrtime,

        },
        url: '/sell/nazelrow2/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "error") {
                alarm('error', 'شماره نازل انتخاب نشده')
                ending(1, error)
            }
            if (resp.message === "success") {

                const tlist1 = resp.mylist[0]


                document.getElementById('id_start').value = tlist1.end
                document.getElementById('id_end').value = tlist1.start
                if (document.getElementById('id_start2')) {
                    document.getElementById('id_start2').value = tlist1.start2
                    document.getElementById('id_end2').value = tlist1.end2
                }
                document.getElementById('id_sell_show').value = tlist1.sell
                if (tlist1.pumpname === 's') {
                    document.getElementById('id_yarane').value = '0'
                    document.getElementById('id_yarane').readOnly = true;
                    document.getElementById('id_azad').readOnly = true;
                    document.getElementById('id_azad').value = '0'
                    document.getElementById('id_ezterari').value = tlist1.ezterari
                }
                if (tlist1.pumpname === 'b') {
                    document.getElementById('nameyar').innerHTML = ' یارانه ایی'
                    document.getElementById('id_yarane').readOnly = false;
                    document.getElementById('id_azad').readOnly = false;
                    document.getElementById('id_yarane').value = tlist1.yarane
                    document.getElementById('id_nimeyarane').value = tlist1.nimeyarane
                    document.getElementById('id_azad').value = tlist1.azad
                    document.getElementById('id_ezterari').value = tlist1.ezterari
                }
                if (tlist1.pumpname === 'm') {
                    document.getElementById('nameyar').innerHTML = ' یارانه ایی'
                    document.getElementById('id_yarane').readOnly = false;
                    document.getElementById('id_azad').readOnly = false;
                    document.getElementById('id_yarane').value = mlist.yarane
                    document.getElementById('id_nimeyarane').value = tlist1.nimeyarane
                    document.getElementById('id_azad').value = mlist.azad
                    document.getElementById('id_ezterari').value = mlist.ezterari
                }

                if (tlist1.pumpname === 'g') {
                    document.getElementById('id_yarane').value = tlist1.yarane
                 document.getElementById('id_nimeyarane').value = tlist1.nimeyarane
                    document.getElementById('id_yarane').readOnly = false;
                    document.getElementById('id_azad').readOnly = false;
                    document.getElementById('id_azad').readOnly = false;
                    document.getElementById('id_ezterari').value = tlist1.ezterari
                    document.getElementById('id_azad').value = tlist1.azad
                }
                document.getElementById('id_ezterari').value = tlist1.ezterari
                document.getElementById('id_azmayesh').value = tlist1.azmayesh
                document.getElementById('id_havale').value = tlist1.havaleh
                document.getElementById('id_sell_show').value = tlist1.sell
                document.getElementById('id_sellkol_show').value = tlist1.sellkol
                document.getElementById('id_ekhtelaf').value = tlist1.ekhtelaf
                document.getElementById('id_mojaz').value = tlist1.mojaz
                document.getElementById('id_nomojaz').value = tlist1.nomojaz
            }
            ending()

        },
        error: function (xhr, status, error) {
            ending(1, error);
        }
    })
}

function clearSell() {
    document.getElementById('id_start').value = ''
    if (document.getElementById('id_start2')) {
        document.getElementById('id_start2').value = ''
    }
    document.getElementById('id_end').value = ''
    if (document.getElementById('id_end2')) {
        document.getElementById('id_end2').value = ''
    }
    document.getElementById('id_yarane').value = ''
    document.getElementById('id_nimeyarane').value = ''
    document.getElementById('id_azad').value = ''
    document.getElementById('id_ezterari').value = ''
    document.getElementById('id_azmayesh').value = '0'
    document.getElementById('id_havale').value = '0'
    document.getElementById('id_sell_show').value = ''
    document.getElementById('id_sellkol_show').value = ''
    document.getElementById('id_ekhtelaf').value = ''
    document.getElementById('id_mojaz').value = ''
    document.getElementById('id_nomojaz').value = ''
}

function showdateSell() {

    var gsid = document.getElementById('id_mygsid').value
    var tarikh = document.getElementById('select').value


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'tarikh': tarikh,

            'gsid': gsid,
        },
        url: '/api/showdateSell/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {

            }
            $('#tableSell tbody').empty()
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                var content = '';
                content += '<tr id=' + mlist.tolombeinfo + '>'

                content += '<td  class="text-center">' + mlist.pumpnumber + '</td>'
                content += '<td class="text-center">' + mlist.end + '</td>'
                content += '<td class="text-center">' + mlist.start + '</td>'
                content += '<td class="text-center">' + mlist.sell + '</td>'
                content += '<td class="text-center">' + mlist.sellkol + '</td>'
                content += '<td class="text-center">' + mlist.ekhtelaf + '</td>'
                content += '<td class="text-center">' + mlist.mojaz + '</td>'
                if (mlist.nomojaz === '0.00') {
                    content += '<td class="text-center">' + mlist.nomojaz + '</td>'
                } else {
                    content += '<td style="background: #ee4a4e; color: #0b0b0b" class="text-center">' + mlist.nomojaz + '</td>'
                }
                $('#tableSell tbody').append(content);
            }
            const summlist = resp.sumlist[0]


            document.getElementById('id_summek').value = summlist.summek
            document.getElementById('id_sumelk').value = summlist.sumelk
            document.getElementById('id_num_show').options.selectIndex = 0
        }
    })
}

function showdateSell2() {
    waiting()
    var gsid = document.getElementById('gs_id').value
    var tarikh = document.getElementById('select').value
    var tarikh2 = document.getElementById('select2').value
    var tarikh3 = document.getElementById('select3').value


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'tarikh': tarikh,
            'tarikh2': tarikh2,
            'tarikh3': tarikh3,
            'gsid': gsid,

        },
        url: '/api/showdateSell2/',
        dataType: "json",
        success: function (resp) {

            $('#tableSell tbody').empty()
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                var content = '';
                content += '<tr id=' + mlist.tolombeinfo + '>'

                content += '<td class="text-center">' + mlist.pumpnumber + '</td>'
                content += '<td class="text-center">' + mlist.end + '</td>'
                content += '<td class="text-center">' + mlist.start + '</td>'
                content += '<td class="text-center">' + mlist.sell + '</td>'
                content += '<td class="text-center">' + mlist.sellkol + '</td>'
                content += '<td class="text-center">' + mlist.ekhtelaf + '</td>'
                content += '<td class="text-center">' + mlist.mojaz + '</td>'
                if (mlist.nomojaz === '0.00') {
                    content += '<td class="text-center">' + mlist.nomojaz + '</td>'
                } else {
                    content += '<td style="background: #ee4a4e; color: #0b0b0b" class="text-center">' + mlist.nomojaz + '</td>'
                }
                $('#tableSell tbody').append(content);

            }
            var context = ""
            if (resp.expire[0]) {
                context = "<div style='background-color: #fbff75'>"
                context += "<ul>"
                context += "<h5>فروش دوره (های)  </h5>"
                for (obje in resp.expire) {
                    const mliste = resp.expire[obje]
                    context += "<h4>" + mliste.ex + "</h4>"
                }
                context += " <h5 class='text-danger'> باید حذف گردد. </h5>"
                context += "</ul>"
                context += "</div>"
                context += "</div>"

                document.getElementById('alertsell').innerHTML = context


            } else {

                document.getElementById('alertsell').innerHTML = ''
            }
            const summlist = resp.sumlist[0]


            document.getElementById('id_summek').value = summlist.summek
            document.getElementById('id_sumelk').value = summlist.sumelk
            document.getElementById('id_num_show').options.selectIndex = 0
            ending()
        },

        error: function () {
            ending(1, error);
        }
    })
}


function pumplist() {
    var gsid = document.getElementById('gs_id').value
    $.ajax({
        type: 'GET',
        data: {

            'gsid': gsid,
        },
        url: '/sell/pumplist/',
        dataType: "json",
        success: function (resp) {
            var content = '';
            if (resp.message === "success") {

            }
            $('#id_num_show').empty()
            $('#tarikh_id').empty()
            content += '<option value="-">یک نازل انتخاب کنید</option>'
            content += '<option value="0">همه نازل ها</option>'
            $('#id_num_show').append(content);
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                content = '';

                content += '<option value="' + mlist.id + '">' + mlist.number + ' - ' + mlist.product + '</option>'
                $('#id_num_show').append(content);
            }

        }
    })
}

function crashpump(val1, val2, val3) {

    var gsid = document.getElementById('gs_id').value
    var tdate = document.getElementById('datecheck').value
    if (val3 > val2) {
        alarm('error', 'تاریخ هارد کرش نباید جلوتر یا مساوی  تاریخ اولین معتبر بعد باشد')
        showdateSell2()
        return false;
    }
    if (val3 < val1) {
        alarm('error', 'تاریخ هارد کرش نباید کمتر یا مساوی  تاریخ آخرین معتبر قبل باشد')
        showdateSell2()
        return false;
    }
    if (tdate < val2) {
        document.getElementById('isshowsell').style.display = 'none'
        document.getElementById('isshowmojodi').style.display = 'none'
        alarm('error', 'تاریخ فروش نباید جلوتر از تاریخ روز جاری باشد')
        showdateSell2()
        return false;
    }
    document.getElementById('isshowsell').style.display = 'block'
    showdateSell2()
    showNazelId2(1)

}

function checkDate(val) {
    var gsid = document.getElementById('id_mygsid').value
    var tdate = document.getElementById('datecheck').value

    if (val < '1402/07/06') {

        document.getElementById('id_yarane').removeAttribute('readonly')
        document.getElementById('id_yarane').removeAttribute('disabled')

        document.getElementById('id_azad').removeAttribute('readonly')
        document.getElementById('id_azad').removeAttribute('disabled')

        document.getElementById('id_ezterari').removeAttribute('readonly')
        document.getElementById('id_ezterari').removeAttribute('disabled')

        document.getElementById('id_azmayesh').removeAttribute('readonly')
        document.getElementById('id_azmayesh').removeAttribute('disabled')

        document.getElementById('id_havale').removeAttribute('readonly')
        document.getElementById('id_havale').removeAttribute('disabled')


    }
    if (tdate < val) {
        document.getElementById('isshowsell').style.display = 'none'
        document.getElementById('isshowmojodi').style.display = 'none'
        alarm('error', 'تاریخ فروش نباید جلوتر از تاریخ روز جاری باشد')
        showdateSell()
        return false;
    }

    if (tdate === val) {
        document.getElementById('isshowsell').style.display = 'none'
        document.getElementById('isshowmojodi').style.display = 'none'
        alarm('warning', 'تاریخ فروش نباید تاریخ روز جاری باشد ، فروش صبح امروز مربوط به تاریخ روز گذشته میباشد')
        showdateSell()
    } else {
        $.ajax({
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                'gsid': gsid,
                'val': val,
            },
            url: '/sell/checkEnd/',
            dataType: "json",
            success: function (resp) {
                if (resp.message === "success") {
                    if (resp.isyesterday == false) {
                        alarm('error', 'اسکن رمزینه دوره قبل انجام نشده.')
                        document.getElementById('isshowsell').style.display = 'none'
                        return false;
                    }
                    if (resp.ismek == false) {
                        alarm('error', 'فروش مکانیکی روز قبل بصورت صحیح ثبت نشده.')
                        document.getElementById('isshowsell').style.display = 'none'
                        return false;
                    }
                    if (resp.sell == false) {
                        alarm('error', 'باید ابتدا رمزینه اسکن گردد.')
                        document.getElementById('isshowsell').style.display = 'none'
                        return false;
                    }
                    // if (resp.sell === true) {
                    //      alarm('error', ' یک فروش ثبت شده بعد از تاریخ انتخابی شما وجود دارد برای ویرایش فروش این تاریخ ابتدا باید فروش های بعد را حذف بفرمایید')
                    //     document.getElementById('isshowsell').style.display = 'none'
                    //     document.getElementById('isshowmojodi').style.display = 'none'
                    //     showdateSell()
                    // } else {
                    document.getElementById('isshowsell').style.display = 'block'
                    document.getElementById('isshowmojodi').style.display = 'block'
                    showdateSell()
                    showNazelId(resp.pump)
                    // }
                }
            }
        })
    }
}

function listsellapi() {
    var gsid = document.getElementById('gs_id').value
    var pump = document.getElementById('id_num_show').value
    $.ajax({
        type: 'GET',
        data: {
            'gsid': gsid,
            'pump': pump,
        },
        url: '/api/listsellapi',
        dataType: "json",
        success: function (resp) {
            $('#tarikh_id').empty()
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                var content = '';
                content += '<option value="' + mlist.tarikh + '">' + mlist.tarikh + ' </option>'
                $('#tarikh_id').append(content);
            }

        }
    })
}

function addclosesellapi() {
    waiting()
    var gsid = document.getElementById('gs_id').value
    var pump = document.getElementById('id_num_show').value
    var tarikh = document.getElementById('tarikh_id').value
    var owner = document.getElementById('owner_id').value
    var info = document.getElementById('info_id').value
    var shname = document.getElementById('shname').value
    if (shname.length < 1) {
        alarm('error', 'شماره نامه را وارد کنید')
        return false
    }

    var table = document.getElementById('tab1')
    var rowCount = table.rows.length;
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'gsid': gsid,
            'pump': pump,
            'tarikh': tarikh,
            'owner': owner,
            'shname': shname,
            'info': info,
        },
        url: '/api/addclosesellapi/',
        dataType: "json",
        success: function (resp) {

            const mlist = resp.mylist[0]
            var content = '';
            // $('#tab1 tbody').empty()
            content += '<tr>'
            content += '<td class="text-center">-</td>'
            content += '<td class="text-center">' + mlist.name + '</td>'
            content += '<td class="text-center">' + mlist.gsid + '</td>'
            content += '<td class="text-center">' + mlist.tarikh + '</td>'
            content += '<td class="text-center">' + mlist.owner + '</td>'
            content += '<td class="text-center">' + mlist.pump + '</td>'
            content += '<td class="text-center">' + mlist.active + '</td>'
            content += '</tr>'
            $('#tab1 tbody').append(content);
            ending()
            if (resp.message === 1) {
                alarm('info', 'عملیات با موفقیت انجام شد')
                location.reload();
            } else {
                alarm('error', 'عملیات شکست خورد')
            }

        }, error: function (xhr, status, error) {
            ending(1, error);
        }


    })
}


function systemlog(id, nazel) {

    waiting()
    document.getElementById('sellid').value = id

    $.ajax({
        type: 'GET',
        data: {

            'newid': id,
            'nazel': nazel,


        },
        url: '/api/ticketeventapi/',
        dataType: "json",
        success: function (resp) {
            $('#SyatemTable tbody').empty()

            var content = '';
            // $('#tab1 tbody').empty()
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]

                content += '<tr>'

                content += '<td class="text-center">' + mlist.info + '</td>'
                content += '<td class="text-center">' + mlist.tarikh + '</td>'

                content += '</tr>'
            }
            $('#SyatemTable tbody').append(content);

            $('#UserTable tbody').empty()
            var content = '';

            for (obj in resp.mylist2) {
                const mlist = resp.mylist2[obj]

                content += '<tr>'

                content += '<td class="text-center">' + mlist.info + '</td>'
                content += '<td class="text-center">' + mlist.tarikh + '</td>'
                content += '<td class="text-center">' + mlist.amount + '</td>'


                content += '</tr>'
            }
            $('#UserTable tbody').append(content);


            ending()
            if (resp.message === 1) {
                alarm('info', 'عملیات با موفقیت انجام شد')

            } else {
                alarm('error', 'عملیات شکست خورد')
            }

        }, error: function (xhr, status, error) {
            ending(1, error);
        }


    })
}

function addsystemlog(id, status, amount) {
    waiting()
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'newid': id,
            'status': status,
            'amount': amount,
        },
        url: '/api/addeventapi/',
        dataType: "json",
        success: function (resp) {
            if (resp.message == 'ok') {
                location.reload();
                alarm('info', 'عملیات با موفقیت انجام شد')

            } else {
                alarm('error', 'عملیات شکست خورد')
            }

        }, error: function (xhr, status, error) {
            ending(1, error);
        }
    })
}

function dellsystemlog() {
    _id = document.getElementById('sellid').value
    waiting()
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'newid': _id,

        },
        url: '/api/delleventapi/',
        dataType: "json",
        success: function (resp) {
            if (resp.message == 'ok') {
                location.reload();
                alarm('info', 'عملیات با موفقیت انجام شد')

            } else {
                alarm('error', 'عملیات شکست خورد')
            }

        }, error: function (xhr, status, error) {
            ending(1, error);
        }
    })
}

function getsellweb() {

    _product = document.getElementById('id_label_single').value

    _gsid = document.getElementById('id_gsid').value
    _date = document.getElementById('select').value
    waiting()
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'product-type': _product,
            'gsid': _gsid,
            'period': _date,

        },
        url: '/api/getsellinfoweb/',
        dataType: "json",
        success: function (resp) {
            if (resp.status == 1) {

                alarm('info', 'عملیات با موفقیت انجام شد')
                alarm('success', 'اطلاعاتی فروش ارسال شد')
                ending()
            }
            if (resp.status == 2) {
                alarm('error', 'عملیات شکست خورد' + " ( " + resp.status + " )")
                alarm('info', 'شناسه GSID اشتباه است')
                ending()
            }
            if (resp.status == 12) {
                alarm('error', 'عملیات شکست خورد' + " ( " + resp.status + " )")
                alarm('info', 'حساب فروش این روز بسته نشده')
                ending()
            }
            if (resp.status == 3) {
                alarm('error', 'عملیات شکست خورد' + " ( " + resp.status + " )")
                alarm('info', 'اطلاعاتی ثبت نشده')
                ending()
            }
            if (resp.status == 4) {
                alarm('info', 'عملیات با موفقیت انجام شد' + " ( " + resp.status + " )")
                alarm('success', 'اطلاعاتی هارد کرش ارسال شد')
                ending()
            }
            if (resp.status == 11) {
                alarm('info', 'عملیات با موفقیت انجام شد' + " ( " + resp.status + " )")
                alarm('success', 'اطلاعاتی بازه تعطیلی / تعویض هارد ارسال شد')
                ending()
            }
            if (resp.status == 6) {
                alarm('error', 'عملیات شکست خورد' + " ( " + resp.status + " )")
                alarm('info', ' شمارنده مکانیکی وجود ندارد یا به درستی ثبت نشده')
                ending()
            }

        }, error: function (xhr, status, error) {
            ending(1, error);
        }
    })
}


function checkNazelSarak(val) {
    $('#tableSell tbody').empty()
    var product = document.getElementById('id_product').value

    $.ajax({
        type: 'GET',
        data: {

            'gsid': val,
            'product': product,

        },
        url: '/visit/listnazel/',
        dataType: "json",
        success: function (resp) {
            var content = '';

            $('#id_num_show').empty()
            content += '<option value=0">یک نازل انتخاب کنید</option>'
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]

                content += '<option value="' + mlist.id + '">' + mlist.number + ' - (' + mlist.name + ') </option>'

            }
            $('#id_num_show').append(content);

            // }
        }

    })

}

function showNazelIdSarak(val) {
    waiting()

    var gsid = document.getElementById('id_gs').value
    var tarikh = document.getElementById('id_tarikh').value
    var val = document.getElementById('id_num_show').value
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'val': val,
            'gsid': gsid,
            'tarikh': tarikh,
        },
        url: '/sell/nazelrow/',
        dataType: "json",
        success: function (resp) {
            if (resp.message === "success") {
                const tlist1 = resp.tlist[0]
                const mlist = resp.mylist[0]
                // document.getElementById('id_start').value = mlist.start
                document.getElementById('id_end').value = mlist.end
                if (document.getElementById('id_end2')) {
                    document.getElementById('id_end2').value = mlist.end2
                }
                if (document.getElementById('id_start2')) {
                    document.getElementById('id_star2').value = mlist.start2
                }
                document.getElementById('id_endsell').value = mlist.endsell
                ending()
                document.getElementById("id_start").focus();

            }

        }
    })

}

function saveSellSarak() {
    waiting()


    var gsid = document.getElementById('id_gs').value
    var tarikh = document.getElementById('id_tarikh').value
    var product = document.getElementById('id_product').value
    var val = document.getElementById('id_num_show').value
    var end = document.getElementById('id_end').value
    var endsell = document.getElementById('id_endsell').value
    var start = document.getElementById('id_start').value
    var sell = 0

    if (end.length === 6) {
        max_number = 999999
    }
    if (end.length === 7) {
        max_number = 9999999
    }
    if (end.length === 8) {
        max_number = 99999999
    }
    if (end.length === 9) {
        max_number = 999999999
    }

    if (parseInt(end) > parseInt(start)) {
        sell = max_number - parseInt(end)
        sell = parseInt(sell) + parseInt(start) + 1
    } else {
        sell = parseInt(start) - parseInt(end)

    }


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'val': val,
            'gsid': gsid,
            'tarikh': tarikh,
            'start': start,
            'end': end,
            'endsell': endsell,
            'sell': sell,
            'product': product,
        },
        url: '/visit/savesellsarak/',
        dataType: "json",
        success: function (resp) {


            $('#tableSell tbody').empty()
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                var content = '';
                content += '<tr id=' + mlist.id + '>'

                content += '<td class="text-center">' + mlist.number + '</td>'
                content += '<td class="text-center">' + mlist.end + '</td>'
                content += '<td class="text-center">' + mlist.start + '</td>'
                content += '<td class="text-center">' + mlist.sell + '</td>'

                $('#tableSell tbody').append(content);

            }
            ending()
            document.getElementById("id_sell").value = resp.summsell;
            document.getElementById("id_sell2").value = resp.summsell2;
            document.getElementById('id_start').value = ''
            document.getElementById("id_start").focus();

        }


    })

}

function checkDateSarak() {
    waiting()


    var gsid = document.getElementById('id_gs').value
    checkNazelSarak(gsid)
    var tarikh = document.getElementById('id_tarikh').value
    var product = document.getElementById('id_product').value


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,

            'gsid': gsid,
            'tarikh': tarikh,
            'product': product,

        },
        url: '/visit/loadsellsarak/',
        dataType: "json",
        success: function (resp) {
            document.getElementById('id_mojodi_start').value = resp.start_mojodi
            document.getElementById('id_mojodi_end').value = resp.end_mojodi

            $('#tableSell tbody').empty()
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]
                var content = '';
                content += '<tr id=' + mlist.id + '>'

                content += '<td class="text-center">' + mlist.number + '</td>'
                content += '<td class="text-center">' + mlist.end + '</td>'
                content += '<td class="text-center">' + mlist.start + '</td>'
                content += '<td class="text-center">' + mlist.sell + '</td>'

                $('#tableSell tbody').append(content);

            }
            ending()

            document.getElementById("id_num_show").focus();
            document.getElementById("id_sell").value = resp.summsell;
            document.getElementById("id_sell2").value = resp.summsell2;

        }


    })

}

function gosarak() {
    var gsid = document.getElementById('id_gs').value
    checkDateSarak()
    checkNazelSarak(gsid)

}

function areainzone(val) {
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'zoneid': val,
        },
        url: '/api/areainzone/',
        dataType: "json",
        success: function (resp) {
            var content = '';

            $('#id_area').empty()
            content += '<option value="0">همه</option>'
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]

                content += '<option value="' + mlist.id + '">' + mlist.name + ' </option>'
            }
            $('#id_area').append(content);

            if ($('#id_gs').length) {
                content = '';
                $('#id_gs').empty()
                content += '<option value="0">همه</option>'
                for (obj in resp.gs_list) {
                    const mlist = resp.gs_list[obj]

                    content += '<option value="' + mlist.id + '">' + mlist.gsid + ' - ' + mlist.name + ' </option>'
                }
                $('#id_gs').append(content);
            }
            // }
        }

    })

}


function cityinarea(val) {
if ($('#id_zone').length) {
    var zoneid = document.getElementById('id_zone').value
}else{
    zoneid = "0"
}

    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'areaid': val,
            'zoneid':zoneid,


        },
        url: '/api/cityinarea/',
        dataType: "json",
        success: function (resp) {
            var content = '';

            $('#id_city').empty()
            content += '<option value="0">همه</option>'
            for (obj in resp.mylist) {
                const mlist = resp.mylist[obj]

                content += '<option value="' + mlist.id + '">' + mlist.name + ' </option>'

            }
            $('#id_city').append(content);

            if ($('#id_gs').length) {
                content = '';
                $('#id_gs').empty()
                content += '<option value="0">همه</option>'
                for (obj in resp.gs_list) {
                    const mlist = resp.gs_list[obj]

                    content += '<option value="' + mlist.id + '">' + mlist.gsid + ' - ' + mlist.name + ' </option>'
                }
                $('#id_gs').append(content);
            }
        }

    })

}



function gsincity(val) {
if ($('#id_area').length) {
    var areaid = document.getElementById('id_area').value
}else{
    areaid = "0"
}
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'cityid': val,
            'areaid': areaid,


        },
        url: '/api/gsincity/',
        dataType: "json",
        success: function (resp) {
            var content = '';



            if ($('#id_gs').length) {
                content = '';
                $('#id_gs').empty()
                content += '<option value="0">همه</option>'
                for (obj in resp.gs_list) {
                    const mlist = resp.gs_list[obj]

                    content += '<option value="' + mlist.id + '">' + mlist.gsid + ' - ' + mlist.name + ' </option>'
                }
                $('#id_gs').append(content);
            }
        }

    })

}


function lastselldore(val) {
    waiting()
    const dore = document.getElementById('select').value
    const nazel = document.getElementById('id_num_show').value


    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            'dore': dore,
            'nazel': nazel,
        },
        url: '/api/lastselldore/',
        dataType: "json",
        success: function (resp) {
            document.getElementById('id_end').value = resp.amount
            document.getElementById('ttarikh').setAttribute('title', resp.date)
            SetValue(1)
            ending()
        }, error: function (xhr, status, error) {
            ending(1);
        }
    })

}