const config = {
    csrfToken: document.getElementsByName('csrfmiddlewaretoken')[0]?.value || '',
    apiBase: '/pay/',
    lockApiBase: '/lock/'
};

// ======== توابع کمکی امنیتی ========
const security = {
    // جلوگیری از XSS
    escapeHtml: (text) => {

        return text.toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    // اعتبارسنجی شناسه
    validateId: (id) => {
        return /^\d+$/.test(id);
    },

    // اعتبارسنجی شماره سریال
    validateSerial: (serial) => {
        return /^[a-zA-Z0-9]{10,12}$/.test(serial);
    },

    // اعتبارسنجی پاسخ سرور
    validateResponse: (resp) => {
        return resp && typeof resp === 'object' && resp.message;
    }
};

const csrf = document.getElementsByName('csrfmiddlewaretoken')[0]?.value || '';

function getStore(id) {
    if (!security.validateId(id)) {
        alert('شناسه نامعتبر است');
        return;
    }
    waiting();

    document.getElementById('StoreId').value = id;
    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'id': id,
        }, url: '/pay/getStore/', dataType: "json", success: function (resp) {
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === 'success') {
                var content = '';
                var i = 1;
                $('#myTable tbody').empty();
                for (obj in resp.list) {
                    if (!resp.list.hasOwnProperty(obj)) continue;

                    const mlist = resp.list[obj];
                    if (!mlist || !mlist.id || !mlist.serial) continue;

                    const safeId = security.escapeHtml(mlist.id);
                    const safeSerial = security.escapeHtml(mlist.serial);

                    content += '<tr id="tr' + safeId + '">';
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + safeId + '">';
                    content += '<td>' + parseInt(i) + '</td>';
                    content += '<td>' + safeSerial + '</td>';

                    if (mlist.level === 0) {
                        content += '<td><img src="/static/assets/img/risk/work-started-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته خرابی نداشته" alt=""/></td></tr>';
                    } else if (mlist.level === 1) {
                        content += '<td><img src="/static/assets/img/risk/low-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته یکبار معیوب شد" alt=""/></td></tr>';
                    } else if (mlist.level === 2) {
                        content += '<td><img src="/static/assets/img/risk/medium-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته دو بار معیوب شد" alt=""/></td></tr>';
                    } else if (mlist.level === 3) {
                        content += '<td><img src="/static/assets/img/risk/high-risk-alert-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته بیش از دو بار معیوب شد" alt=""/></td></tr>';
                    }

                    i += 1;
                }
                $('#myTable tbody').append(content);
                getStoretoTek(security.escapeHtml(document.getElementById('id_tek').value));
                ending();
            } else {
                alarm('danger', 'خطا در دریافت اطلاعات');
                ending();
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور');
            ending(1, error);
        }
    });
}

function getStoreTek(id) {
    waiting();

    const StoreId = security.escapeHtml(document.getElementById('StoreId').value);
    var table = document.getElementById('mytab2');

    if (!security.validateId(id) || !security.validateId(StoreId)) {
        alarm('danger', 'شناسه نامعتبر است');
        ending();
        return;
    }

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'id': id, 'StoreId': StoreId,
        }, url: '/pay/getStoreTek/', dataType: "json", success: function (resp) {
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === 'success') {
                var content = '';
                var i = 1;
                $('#mytab2 tbody').empty();
                for (obj in resp.list) {
                    if (!resp.list.hasOwnProperty(obj)) continue;

                    const mlist = resp.list[obj];
                    if (!mlist || !mlist.id || !mlist.serial) continue;

                    const safeId = security.escapeHtml(mlist.id);
                    const safeSerial = security.escapeHtml(mlist.serial);

                    content += '<tr id="tr' + safeId + '">';
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox1" data-id="' + safeId + '">';
                    content += '<td>' + parseInt(i) + '</td>';
                    content += '<td>' + safeSerial + '</td></tr>';
                    i += 1;
                }
                $('#mytab2 tbody').append(content);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)";
                ending();
            } else {
                alarm('danger', 'خطا در دریافت اطلاعات');
                ending();
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور');
            ending(1, error);
        }
    });
}

function getStoretoTek(id) {
    waiting();

    const StoreId = security.escapeHtml(document.getElementById('StoreId').value);
    var table = document.getElementById('mytab2');

    if (!security.validateId(id) || !security.validateId(StoreId)) {
        alarm('danger', 'شناسه نامعتبر است');
        ending();
        return;
    }

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'id': id, 'StoreId': StoreId,
        }, url: '/pay/getStoretoTek/', dataType: "json", success: function (resp) {
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === 'success') {
                var content = '';
                var i = 1;
                $('#mytab2 tbody').empty();
                for (obj in resp.list) {
                    if (!resp.list.hasOwnProperty(obj)) continue;

                    const mlist = resp.list[obj];
                    if (!mlist || !mlist.id || !mlist.serial) continue;

                    const safeId = security.escapeHtml(mlist.id);
                    const safeSerial = security.escapeHtml(mlist.serial);

                    content += '<tr id="tr' + safeId + '">';
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox1" data-id="' + safeId + '">';
                    content += '<td>' + parseInt(i) + '</td>';
                    content += '<td>' + safeSerial + '</td>';
                    content += '<td>' + mlist.status + '</td>';

                    if (mlist.level === 0) {
                        content += '<td><img src="/static/assets/img/risk/work-started-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته خرابی نداشته" alt=""/></td></tr>';
                    } else if (mlist.level === 1) {
                        content += '<td><img src="/static/assets/img/risk/low-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته یکبار معیوب شد" alt=""/></td></tr>';
                    } else if (mlist.level === 2) {
                        content += '<td><img src="/static/assets/img/risk/medium-risk-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته دو بار معیوب شد" alt=""/></td></tr>';
                    } else if (mlist.level === 3) {
                        content += '<td><img src="/static/assets/img/risk/high-risk-alert-icon.svg" data-toggle="tooltip" title="در یک ماه گذشته بیش از دو بار معیوب شد" alt=""/></td></tr>';
                    }

                    i += 1;
                }
                $('#mytab2 tbody').append(content);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)";
                ending();
            } else {
                alarm('danger', 'خطا در دریافت اطلاعات');
                ending();
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور');
            ending(1, error);
        }
    });
}

function AddRow(val) {
    waiting();

    var $this = $(this);
    var table = document.getElementById('mytab2');
    const userid = security.escapeHtml(document.getElementById('id_tek').value);

    if (!security.validateId(userid) || userid === '-1') {
        alarm('warning', 'لطفا ابتدا یک تکنسین را انتخاب کنید');
        ending();
        return false;
    }

    var idsArr2 = [];
    $('.checkbox:checked').each(function () {
        const id = $(this).attr('data-id');
        if (security.validateId(id)) {
            idsArr2.push(id);
        }
    });

    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید');
        ending();
        return false;
    }

    // محدودیت تعداد آیتم‌های انتخاب شده
    if (idsArr2.length > 50) {
        alarm('warning', 'حداکثر 50 آیتم قابل انتخاب است');
        ending();
        return false;
    }

    var strIds2 = idsArr2.join(",");

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': config.csrfToken, 'strIds': strIds2, 'id_tek': userid, 'val': val,
        }, url: config.apiBase + 'AddSTORETEK/', dataType: "json", success: function (resp) {
            if (!security.validateResponse(resp) || !resp.list || !Array.isArray(resp.list)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === 'success') {
                $('.checkbox:checked').each(function (index) {
                    if (index >= resp.list.length) return;

                    $(this).parents("tr").remove();

                    const mlist = resp.list[index];
                    if (!mlist) return;

                    const safeId = security.escapeHtml(mlist.id);
                    const safeSerial = security.escapeHtml(mlist.serial);
                    const safeSt = mlist.st ? security.escapeHtml(mlist.st) : '';

                    var content = '<tr id="tr' + safeId + '">';
                    content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox1" data-id="' + safeId + '">';
                    content += '<td>جدید</td>';
                    content += '<td style="font-size: 20px;">' + safeSerial + '</td>';

                    if (val === 1) {
                        content += '</tr>';
                    }
                    if (val === 2) {
                        content += '<td>' + safeSt + '</td></tr>';
                    }

                    $('#mytab2 tbody').append(content);
                });

                ending();
                alarm('success', 'عملیات بدرستی انجام شد');
                $('.check_all').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)";
            } else {
                ending();
                alarm('danger', 'عملیات شکست خورد: ' + (resp.error || ''));
            }
        }, error: function (xhr, status, error) {
            ending(1, error);
            alarm('danger', 'خطا در ارتباط با سرور');
        }
    });
    return false;
}

function AddGS() {
    waiting();

    const userid = security.escapeHtml(document.getElementById('id_tek').value);
    var table = document.getElementById('mytab2');

    if (!security.validateId(userid) || userid === '-1') {
        alarm('warning', 'لطفا ابتدا یک تکنسین معتبر را انتخاب کنید');
        ending();
        return false;
    }

    var idsArr2 = [];
    $('.checkbox:checked').each(function () {
        const id = $(this).attr('data-id');
        if (security.validateId(id)) {
            idsArr2.push(id);
        }
    });

    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید');
        ending();
        return false;
    }

    // محدودیت تعداد آیتم‌های انتخاب شده
    if (idsArr2.length > 50) {
        alarm('warning', 'حداکثر 50 آیتم قابل انتخاب است');
        ending();
        return false;
    }

    var strIds2 = idsArr2.join(",");

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'strIds': strIds2, 'id_tek': userid,
        }, url: '/pay/AddSTOREGS/', dataType: "json", success: function (resp) {
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === 'success') {
                $('.checkbox:checked').each(function () {
                    $(this).parents("tr").remove();
                });

                alarm('success', 'عملیات بدرستی انجام شد');
                $('.check_all').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)";
                ending();
            } else {
                alarm('danger', 'عملیات شکست خورد: ' + (resp.error || ''));
                ending();
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور');
            ending(1, error);
        }
    });
    return false;
}

function RemoveRow(val) {
    waiting();

    const userid = security.escapeHtml(document.getElementById('id_tek').value);
    var tablep = document.getElementById('tblpost');
    var table = document.getElementById('mytab2');

    if (!security.validateId(userid)) {
        alarm('warning', 'شناسه تکنسین نامعتبر است');
        ending();
        return false;
    }

    var idsArr2 = [];
    $('.checkbox1:checked').each(function () {
        const id = $(this).attr('data-id');
        if (security.validateId(id)) {
            idsArr2.push(id);
        }
    });

    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید');
        ending();
        return false;
    }

    // محدودیت تعداد آیتم‌های انتخاب شده
    if (idsArr2.length > 50) {
        alarm('warning', 'حداکثر 50 آیتم قابل انتخاب است');
        ending();
        return false;
    }

    var strIds2 = idsArr2.join(",");

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'strIds': strIds2, 'userid': userid, 'val': val,
        }, url: '/pay/RemoveSTORETEK/', dataType: "json", success: function (resp) {
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === "success") {
                $('.checkbox1:checked').each(function (index) {
                    if (index >= (resp.list || []).length) return;

                    $(this).parents("tr").remove();

                    if (resp.val !== '3') {
                        const mlist = resp.list[index];
                        if (!mlist) return;

                        const safeId = security.escapeHtml(mlist.id);
                        const safeSerial = security.escapeHtml(mlist.serial);
                        const safeSt = mlist.st ? security.escapeHtml(mlist.st) : '';
                        const safeUser = mlist.user ? security.escapeHtml(mlist.user) : '';

                        var content = '<tr id="tr' + safeId + '">';
                        content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + safeId + '">';
                        content += '<td>برگشت خورده</td>';
                        content += '<td style="font-size: 20px;">' + safeSerial + '</td>';

                        if (val === 2) {
                            content += '<td>' + safeSt + '</td>';
                            content += '<td>' + safeUser + '</td>';
                        }

                        content += '</tr>';
                        $('#myTable tbody').append(content);
                    } else {
                        const mlist = resp.list[index];
                        if (!mlist) return;

                        const safeId = security.escapeHtml(mlist.id);
                        const safeSerial = security.escapeHtml(mlist.serial);
                        const safeSt = mlist.st ? security.escapeHtml(mlist.st) : '';
                        const safeUser = mlist.user ? security.escapeHtml(mlist.user) : '';

                        var content = '<tr id="tr' + safeId + '">';
                        content += '<td class="align-middle text-center text-sm"><input type="checkbox" class="checkbox" data-id="' + safeId + '">';
                        content += '<td>جدید</td>';
                        content += '<td style="font-size: 20px;">' + safeSerial + '</td>';

                        if (val === 2) {
                            content += '<td>' + safeSt + '</td>';
                            content += '<td>' + safeUser + '</td>';
                        }

                        content += '</tr>';
                        $('#tblpost tbody').append(content);
                    }
                });

                alarm('success', 'عملیات بدرستی انجام شد');
                ending();
                $('.check_alldell').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)";
                document.getElementById('countpost').innerText = "(" + tablep.tBodies[0].rows.length + "مورد)";

            } else {
                alarm('danger', 'عملیات شکست خورد: ' + (resp.error || ''));
                ending();
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور');
            ending(1, error);
        }
    });
    ending();
    return false;
}

function CheckSerial(serial, id, st) {
    waiting();

    if (!security.validateSerial(serial)) {
        ending();
        alarm('danger', 'شماره سریال نامعتبر است');
        return false;
    }

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf,
            'serial': security.escapeHtml(serial),
            'id': security.escapeHtml(id),
            'st': security.escapeHtml(st),
        }, url: '/pay/checkserial/', dataType: "json", success: function (resp) {
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === "level2" || resp.message === "level3") {
                ending();
                alarm('error', resp.payam || 'خطا در بررسی سریال');
                return false;
            }

            if (resp.message === "success") {
                document.getElementById('lblId').textContent = " تعداد " + (resp.tedad || 0);

                if (!resp.mylist || !resp.mylist[0]) {
                    ending();
                    return;
                }

                const mlist = resp.mylist[0];
                const safeId = security.escapeHtml(mlist.id);
                const safeSerial = security.escapeHtml(mlist.serial);

                var table = document.getElementById("listTable");
                var row = table.insertRow(0);
                row.id = "r" + safeId;

                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
                var cell3 = row.insertCell(2);

                cell1.textContent = safeSerial;

                if (id === 0) {
                    cell2.innerHTML = "<a onclick=\"removehis2(" + safeId + ")\" class=\"btn btn-warning\"> حذف</a>";
                } else {
                    cell2.innerHTML = "<a onclick=\"removehis(" + safeId + ")\" class=\"btn btn-warning\"> حذف</a>";
                }

                cell3.innerHTML = "<a style='color: white' onclick=\"addstore(" + safeId + ")\" data-target=\"#addstorefun\" data-toggle=\"modal\" class=\"btn btn-primary\">قطعات مصرفی</a>";

                ending();
            } else {
                ending();
                alarm('danger', 'خطا در پردازش درخواست');
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور');
            ending(1, error);
        }
    });
    return false;
}

function plusstore(val, val2) {
    waiting();

    const storeid = security.escapeHtml(document.getElementById('store_id_fun').value);

    if (!security.validateId(val) || !security.validateId(storeid)) {
        alarm('danger', 'مقادیر ورودی نامعتبر است');
        ending();
        return;
    }

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf,
            'val': security.escapeHtml(val),
            'val2': security.escapeHtml(val2),
            'storeid': storeid,
        }, url: '/pay/plusstore/', dataType: "json", success: function (resp) {
            if (!resp || typeof resp.newval === 'undefined') {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            document.getElementById('id_value-' + val).value = security.escapeHtml(resp.newval.toString());
            ending();
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور');
            ending(1, error);
        }
    });
}

function addstore(val) {
    waiting();

    // اعتبارسنجی ورودی
    if (!security.validateId(val)) {
        alarm('danger', 'شناسه نامعتبر است');
        ending();
        return;
    }

    // تنظیم مقدار با پاک‌سازی
    document.getElementById('store_id_fun').value = security.escapeHtml(val);

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'id': val,
        }, url: '/pay/addstorefunc/', dataType: "json", success: function (resp) {
            // اعتبارسنجی پاسخ سرور
            if (!security.validateResponse(resp) || !resp.storename || !Array.isArray(resp.storename) || !resp.mylist || !Array.isArray(resp.mylist)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            // پاک‌سازی و ایجاد محتوای ایمن برای بخش قطعات
            $('#id_repairstore').empty();
            var content = '';

            resp.storename.forEach(mlist => {
                if (!mlist || !mlist.id || !mlist.name || typeof mlist.tedad === 'undefined') return;

                const safeId = security.escapeHtml(mlist.id);
                const safeName = security.escapeHtml(mlist.name);
                const safeTedad = security.escapeHtml(mlist.tedad.toString());

                content += `
                    <div class="row">
                        <div class="col-2">
                            <button onclick="plusstore(${safeId},2)" class="btn btn-danger">-</button>
                        </div>
                        <div class="col-3">
                            <input readonly id="id_value-${safeId}" class="form-control text-primary text-center" value="${safeTedad}">
                        </div>
                        <div class="col-6">
                            <button onclick="plusstore(${safeId},1)" class="btn btn-success">${safeName}</button>
                        </div>
                    </div>
                    <br>
                `;
            });

            $('#id_repairstore').append(content);

            // پاک‌سازی و ایجاد محتوای ایمن برای جدول
            $('#tableaddstore tbody').empty();
            var tableContent = '';

            resp.mylist.forEach(mlist => {
                if (!mlist || !mlist.id || !mlist.name || typeof mlist.count === 'undefined') return;

                const safeId = security.escapeHtml(mlist.id);
                const safeName = security.escapeHtml(mlist.name);
                const safeCount = security.escapeHtml(mlist.count.toString());

                tableContent += `
                    <tr id="r${safeId}">
                        <td>${safeName}</td>
                        <td>${safeCount}</td>
                        <td>
                            <a style="color: #f3fdf3" onclick="deletezone_repaire_store(${safeId})" class="btn nav-link bg-danger">حذف</a>
                        </td>
                    </tr>
                `;
            });

            $('#tableaddstore tbody').append(tableContent);
            ending();
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور: ' + security.escapeHtml(error));
            ending(1, error);
        }
    });
}

function deletezone_repaire_store(val) {
    waiting();

    // اعتبارسنجی ورودی
    if (!security.validateId(val)) {
        alarm('danger', 'شناسه نامعتبر است');
        ending();
        return;
    }

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'id': val,
        }, url: '/pay/delete_store_item/', dataType: "json", success: function (resp) {
            // اعتبارسنجی پاسخ سرور
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            // حذف ایمن عنصر از DOM
            const element = document.getElementById('r' + security.escapeHtml(val));
            if (element) {
                element.remove();
            }

            alarm('info', 'قطعه مورد نظر بدرستی حذف شد');
            ending();
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور: ' + security.escapeHtml(error));
            ending(1, error);
        }
    });
}

function newstore() {
    waiting();

    // دریافت و اعتبارسنجی ورودی‌ها
    const store = security.escapeHtml(document.getElementById('store_id_fun').value);
    const name = security.escapeHtml(document.getElementById('id_repairstore').value);
    const amount = security.escapeHtml(document.getElementById('id_amount').value);

    if (!security.validateId(store) || !name || !amount) {
        alarm('danger', 'مقادیر ورودی نامعتبر است');
        ending();
        return;
    }

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'store': store, 'name': name, 'amount': amount,
        }, url: '/pay/newstorefun/', dataType: "json", success: function (resp) {
            // اعتبارسنجی پاسخ سرور
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            alarm('info', 'عملیات با موفقیت انجام شد.');
            // فراخوانی ایمن تابع addstore
            if (security.validateId(store)) {
                addstore(store);
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور: ' + security.escapeHtml(error));
            ending(1, error);
        }
    });
}

function removehis(val) {
    // اعتبارسنجی ورودی
    if (!security.validateId(val)) {
        alarm('danger', 'شناسه نامعتبر است');
        return false;
    }

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'id': val,
        }, url: '/pay/removeSerial/', dataType: "json", success: function (resp) {
            // اعتبارسنجی پاسخ سرور
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                return;
            }

            if (resp.message === "success") {
                // حذف ایمن عنصر از DOM
                const element = document.getElementById('r' + security.escapeHtml(val));
                if (element) {
                    element.remove();
                }

                alarm('info', 'با موفقیت حذف شد');
                document.getElementById('lblId').textContent = " تعداد " + (security.escapeHtml(resp.tedad) || 0);
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور: ' + security.escapeHtml(error));
        }
    });
    return false;
}

function removehis2(val) {
    // اعتبارسنجی ورودی
    if (!security.validateId(val)) {
        alarm('danger', 'شناسه نامعتبر است');
        return false;
    }

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'id': val,
        }, url: '/pay/removeSerial2/', dataType: "json", success: function (resp) {
            // اعتبارسنجی پاسخ سرور
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                return;
            }

            if (resp.message === "success") {
                // حذف ایمن عنصر از DOM
                const element = document.getElementById('r' + security.escapeHtml(val));
                if (element) {
                    element.remove();
                }

                alarm('info', 'با موفقیت حذف شد');
                document.getElementById('lblId').textContent = " تعداد " + (security.escapeHtml(resp.tedad) || 0);
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور: ' + security.escapeHtml(error));
        }
    });
    return false;
}

function AddRowlock(val) {
    waiting();

    // دریافت و اعتبارسنجی ورودی‌ها
    const userid = security.escapeHtml(document.getElementById('id_tek').value);
    var table = document.getElementById('mytab2');

    if (!security.validateId(userid) || userid === '-1') {
        alarm('warning', 'لطفا ابتدا یک تکنسین معتبر را انتخاب کنید');
        ending();
        return false;
    }

    // جمع‌آوری و اعتبارسنجی آیتم‌های انتخاب شده
    var idsArr2 = [];
    $('.checkbox:checked').each(function () {
        const id = $(this).attr('data-id');
        if (security.validateId(id)) {
            idsArr2.push(id);
        }
    });

    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید');
        ending();
        return false;
    }

    // محدودیت تعداد آیتم‌های انتخاب شده
    if (idsArr2.length > 50) {
        alarm('warning', 'حداکثر 50 آیتم قابل انتخاب است');
        ending();
        return false;
    }

    var strIds2 = idsArr2.join(",");

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'strIds': strIds2, 'id_tek': userid, 'val': val,
        }, url: '/lock/addlocktek/', dataType: "json", success: function (resp) {
            // اعتبارسنجی پاسخ سرور
            if (!security.validateResponse(resp) || !resp.list || !Array.isArray(resp.list)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === 'success') {
                $('.checkbox:checked').each(function (index) {
                    if (index >= resp.list.length) return;

                    $(this).parents("tr").remove();

                    const mlist = resp.list[index];
                    if (!mlist) return;

                    // پاک‌سازی داده‌ها قبل از نمایش
                    const safeId = security.escapeHtml(mlist.id);
                    const safeSerial = security.escapeHtml(mlist.serial);
                    const safeSt = mlist.st ? security.escapeHtml(mlist.st) : '';
                    const safeUser = mlist.user ? security.escapeHtml(mlist.user) : '';

                    // ایجاد محتوای ایمن
                    var content = `
                        <tr id="tr${safeId}">
                            <td class="align-middle text-center text-sm">
                                <input type="checkbox" class="checkbox1" data-id="${safeId}">
                            </td>
                            <td>جدید</td>
                            <td style="font-size: 20px;">${safeSerial}</td>
                    `;

                    if (val === 2) {
                        content += `<td>${safeSt}</td>`;
                    }

                    content += `
                            <td style="font-size: 20px;">${safeUser}</td>
                        </tr>
                    `;

                    $('#mytab2 tbody').append(content);
                });

                ending();
                alarm('success', 'عملیات بدرستی انجام شد');
                $('.check_all').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)";
            } else {
                ending();
                alarm('danger', 'عملیات شکست خورد: ' + (resp.error || ''));
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور: ' + security.escapeHtml(error));
            ending(1, error);
        }
    });
    return false;
}

function RemoveRowlock(val) {
    waiting();

    // دریافت و اعتبارسنجی ورودی‌ها
    const userid = security.escapeHtml(document.getElementById('id_tek').value);
    var tablep = document.getElementById('tblpost');
    var table = document.getElementById('mytab2');

    if (!security.validateId(userid)) {
        alarm('warning', 'شناسه تکنسین نامعتبر است');
        ending();
        return false;
    }

    // جمع‌آوری و اعتبارسنجی آیتم‌های انتخاب شده
    var idsArr2 = [];
    $('.checkbox1:checked').each(function () {
        const id = $(this).attr('data-id');
        if (security.validateId(id)) {
            idsArr2.push(id);
        }
    });

    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید');
        ending();
        return false;
    }

    // محدودیت تعداد آیتم‌های انتخاب شده
    if (idsArr2.length > 50) {
        alarm('warning', 'حداکثر 50 آیتم قابل انتخاب است');
        ending();
        return false;
    }

    var strIds2 = idsArr2.join(",");

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'strIds': strIds2, 'userid': userid, 'val': val,
        }, url: '/lock/removelocktek/', dataType: "json", success: function (resp) {
            // اعتبارسنجی پاسخ سرور
            if (!security.validateResponse(resp)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === "success") {
                $('.checkbox1:checked').each(function (index) {
                    if (index >= (resp.list || []).length) return;

                    $(this).parents("tr").remove();

                    if (resp.val !== '3') {
                        const mlist = resp.list[index];
                        if (!mlist) return;

                        // پاک‌سازی داده‌ها قبل از نمایش
                        const safeId = security.escapeHtml(mlist.id);
                        const safeSerial = security.escapeHtml(mlist.serial);
                        const safeSt = mlist.st ? security.escapeHtml(mlist.st) : '';
                        const safeUser = mlist.user ? security.escapeHtml(mlist.user) : '';

                        // ایجاد محتوای ایمن
                        var content = `
                            <tr id="tr${safeId}">
                                <td class="align-middle text-center text-sm">
                                    <input type="checkbox" class="checkbox" data-id="${safeId}">
                                </td>
                                <td>برگشت خورده</td>
                                <td style="font-size: 20px;">${safeSerial}</td>
                        `;

                        if (val === 2) {
                            content += `
                                <td>${safeSt}</td>
                                <td>${safeUser}</td>
                            `;
                        }

                        content += `</tr>`;
                        $('#myTable tbody').append(content);
                    } else {
                        const mlist = resp.list[index];
                        if (!mlist) return;

                        // پاک‌سازی داده‌ها قبل از نمایش
                        const safeId = security.escapeHtml(mlist.id);
                        const safeSerial = security.escapeHtml(mlist.serial);
                        const safeSt = mlist.st ? security.escapeHtml(mlist.st) : '';
                        const safeUser = mlist.user ? security.escapeHtml(mlist.user) : '';

                        // ایجاد محتوای ایمن
                        var content = `
                            <tr id="tr${safeId}">
                                <td class="align-middle text-center text-sm">
                                    <input type="checkbox" class="checkbox" data-id="${safeId}">
                                </td>
                                <td>جدید</td>
                                <td style="font-size: 20px;">${safeSerial}</td>
                        `;

                        if (val === 2) {
                            content += `
                                <td>${safeSt}</td>
                                <td>${safeUser}</td>
                            `;
                        }

                        content += `</tr>`;
                        $('#tblpost tbody').append(content);
                    }
                });

                alarm('success', 'عملیات بدرستی انجام شد');
                $('.check_alldell').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)";
                document.getElementById('countpost').innerText = "(" + tablep.tBodies[0].rows.length + "مورد)";
                ending();
            } else {
                alarm('danger', 'عملیات شکست خورد: ' + (resp.error || ''));
                ending();
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور: ' + security.escapeHtml(error));
            ending(1, error);
        }
    });
    return false;
}

function AddRowlock2(val) {
    waiting();

    // دریافت و اعتبارسنجی ورودی‌ها
    const userid = security.escapeHtml(document.getElementById('id_tek').value);
    const userid2 = security.escapeHtml(document.getElementById('id_tek2').value);
    var table = document.getElementById('mytab2');

    if (!security.validateId(userid) || userid === '-1') {
        alarm('warning', 'لطفا ابتدا یک تکنسین معتبر را انتخاب کنید');
        ending();
        return false;
    }

    // جمع‌آوری و اعتبارسنجی آیتم‌های انتخاب شده
    var idsArr2 = [];
    $('.checkbox:checked').each(function () {
        const id = $(this).attr('data-id');
        if (security.validateId(id)) {
            idsArr2.push(id);
        }
    });

    if (idsArr2.length < 1) {
        alarm('warning', 'لطفا ابتدا یک آیتم را انتخاب کنید');
        ending();
        return false;
    }

    // محدودیت تعداد آیتم‌های انتخاب شده
    if (idsArr2.length > 50) {
        alarm('warning', 'حداکثر 50 آیتم قابل انتخاب است');
        ending();
        return false;
    }

    var strIds2 = idsArr2.join(",");

    $.ajax({
        type: 'POST', data: {
            'csrfmiddlewaretoken': csrf, 'strIds': strIds2, 'id_tek': userid, 'id_tek2': userid2, 'val': val,
        }, url: '/lock/addlocktek2/', dataType: "json", success: function (resp) {
            // اعتبارسنجی پاسخ سرور
            if (!security.validateResponse(resp) || !resp.list || !Array.isArray(resp.list)) {
                alarm('danger', 'پاسخ سرور نامعتبر است');
                ending();
                return;
            }

            if (resp.message === 'success') {
                $('.checkbox:checked').each(function (index) {
                    if (index >= resp.list.length) return;

                    $(this).parents("tr").remove();

                    const mlist = resp.list[index];
                    if (!mlist) return;

                    // پاک‌سازی داده‌ها قبل از نمایش
                    const safeId = security.escapeHtml(mlist.id);
                    const safeSerial = security.escapeHtml(mlist.serial);
                    const safeSt = mlist.st ? security.escapeHtml(mlist.st) : '';
                    const safeUser = mlist.user ? security.escapeHtml(mlist.user) : '';

                    // ایجاد محتوای ایمن
                    var content = `
                        <tr id="tr${safeId}">
                            <td class="align-middle text-center text-sm">
                                <input type="checkbox" class="checkbox1" data-id="${safeId}">
                            </td>
                            <td>جدید</td>
                            <td style="font-size: 20px;">${safeSerial}</td>
                    `;

                    if (val === 2) {
                        content += `<td>${safeSt}</td>`;
                    }

                    content += `
                            <td style="font-size: 20px;">${safeUser}</td>
                        </tr>
                    `;

                    $('#mytab2 tbody').append(content);
                });

                ending();
                alarm('success', 'عملیات بدرستی انجام شد');
                $('.check_all').prop('checked', false);
                document.getElementById('countgs').innerText = "(" + table.tBodies[0].rows.length + "مورد)";
            } else {
                ending();
                alarm('danger', 'عملیات شکست خورد: ' + (resp.error || ''));
            }
        }, error: function (xhr, status, error) {
            alarm('danger', 'خطا در ارتباط با سرور: ' + security.escapeHtml(error));
            ending(1, error);
        }
    });
    return false;
}