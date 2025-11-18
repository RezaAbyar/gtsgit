const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

function SaveAddGs(){
    var $this = $(this);
    let url = '/api/creategs/'
    let gsidGs = document.getElementById('gsidgs').value
    let nameGs = document.getElementById('namegs').value
    let addressGs = document.getElementById('addressgs').value
    let tellGs = document.getElementById('tellgs').value
    let master = document.getElementById('Master').value
    let id_area = document.getElementById('id_narea').value
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken' :csrf,
            'gsid': gsidGs,
            'name': nameGs,
            'address': addressGs,
            'phone': tellGs,
            'area': id_area,
        },
        url: url,
        dataType: "json",
         }).done(function (data) {
   const mlist = data.mylist[0]
        var content ='';

        content += '<td>' + mlist.gsid + '</td>';
        content += '<td>'+mlist.name+'</td>';
        content += '<td>'+mlist.zone+'</td>';
        content += '<td>'+mlist.area+'</td>';
        content += '<td>'+mlist.address+'</td>';
        content += '<td>'+mlist.tell+'</td>';
        content += ' <td style="width: 45%">'
        content += '<a style="color: #f6f7ff" href="#" class="btn nav-link bg-info-bright" title="مشخصات مالک" onclick="getMalek('+mlist.id+')" data-toggle="modal"><i data-feather="list" aria-hidden="true"></i>مالک </a>'
        content += '<a style="color: #f6f7ff" href="#" class="btn nav-link bg-secondary-bright" title="لیست نازل ها"\n' +
            '                       onclick="getMalek('+mlist.id+')" data-toggle="modal" data-target="#exampleModal1">\n' +
            '                        نازلها\n' +
            '                    </a>'
        content +=' <a style="color: #f6f7ff" href="#" class="btn nav-link bg-warning-bright" title="ویرایش"\n' +
            '                       onclick="getMalek('+mlist.id+')" data-toggle="modal" data-target="#exampleModal1">\n' +
            '                        <i data-feather="edit" aria-hidden="true"></i>\n' +
            '                    </a>'
        content += '</td>'
         $('#myTable tbody').append(content);
          })
    alarm('success','عملیات موفق ، جایگاه به درستی ایجاد شد')
 };
function ChangeRole() {
    const MyRole = document.getElementById('Mylad')
    id = MyRole.value
    document.getElementById('userZone').style.display = "none";
    document.getElementById('userArea').style.display = "none";
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
}
function ZoneArea(){
    const AreaZone = document.getElementById('Master')
    $('#Detail').empty();
    var myTag = AreaZone.value;
    let url = '/api/zonearea/' + myTag
    $.ajax({
        type: 'GET',
        dataType: "json",
        url: url,
    }).done(function (data) {
        for (obj in data.mylist) {
            const mlist = data.mylist[obj]
            var content = '';
            content += '<option value=' + mlist.id + '>' + mlist.name + '</option>';
            $('#Detail').append(content);
        }
    })
};
function SaveOwner(){
    codemeli = document.getElementById('id_codemeli').value
    Password1 = document.getElementById('Password1').value
    id_name = document.getElementById('id_name').value
    id_lname = document.getElementById('id_lname').value
    id_mobail = document.getElementById('id_mobail').value
    userZone = document.getElementById('Master').value
    userArea = document.getElementById('Detail').value
    Mylad = document.getElementById('Mylad').value

    let url = '/api/createowner/'
    $.ajax({
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf,
            'name': id_name,
            'codemeli': codemeli,
            'Password1': Password1,
            'lname': id_lname,
            'mobail': id_mobail,
            'zone': userZone,
            'area': userArea,
            'role': Mylad,
        },
        dataType: "json",
        url: url,
    }).done(function (data) {

        const mlist = data.mylist[0]


        var content = '';
        content += '<tr>';
        content += '<td>' + mlist.info + '</td>';
        content += '<td>' + mlist.codemeli + '</td>';
        content += '<td>' + mlist.role + '</td>';
        content += '<td>' + mlist.date + '</td>';
        content += '<td>' + mlist.active + '</td>';


        content += '<button style="color: #f3fdf3" id="editUsernow" onclick="" class="btn nav-link bg-warning">  ویرایش</button></td>'

        if (mlist.roleid === 'gs') {
            content += '<td><button style="color: #f3fdf3" id="listGs" onclick=""\n' +
                '                        class="btn nav-link bg-secondary">  جایگاه ها\n' +
                '                </button>'
        }

        if (mlist.roleid === 'tek') {
            content += '<td><button style="color: #f3fdf3" id="listGs" onclick="" class="btn nav-link bg-secondary">  جایگاه ها</button>'
        }
        content += '</tr>';

        $('#myTable tbody').append(content);
        alarm('success','عملیات موفق ، کاربر به درستی ایجاد شد')

    })
};