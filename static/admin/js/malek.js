const inputCard = document.getElementById('SaveUserId')
const EditUser = document.getElementById('editUser')
const EditBtn = document.getElementById('SaveEditUserId')
const AreaZone = document.getElementById('Master')
const SaveAddGs = document.getElementById('SaveAddGs')
const SaveNazelAdd = document.getElementById('SaveNazelAdd')
const inputState = document.getElementById('inputState')
const Mylad = document.getElementById('Mylad')
const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
function getMalek(val) {

    document.getElementById('IdGs').value=val;
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

        var content ='';
        content += '<tr id="' + 1 + '">';
        content += '<td id="fname">' + mlist.name + '</td>';
        content += '<td id="lname">'+mlist.lname+'</td>';
        content += '<td id="cmeli">'+mlist.codemeli+'</td>';
        content += '<td id="tell">'+mlist.mobail+'</td>';


         $('#tblList tbody').append(content);
          }
}else{
      $('#createUser').modal('show');
  }
 });
}




inputCard.addEventListener('click', e => {

    e.preventDefault();
    var $this = $(this);
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
                 alarm('success','عملیات موفق ، ')
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

    document.getElementById('CodMeli1').value=document.getElementById('cmeli').innerText

   document.getElementById('firstNameId1').value=document.getElementById('fname').innerText
    document.getElementById('lastNameId1').value=document.getElementById('lname').innerText
  document.getElementById('mobailId1').value=document.getElementById('tell').innerText
});

EditBtn.addEventListener('click', e => {

    e.preventDefault();
    var $this = $(this);
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
             getMalek(IdGs)
            } else {
               getMalek(IdGs)

            }
        }
    });
    return false;
});


function getArea(){

        var myTag = document.getElementById('Master').value

    $('#id_area1').empty();

    let url = '/ZoneArea/'
$.ajax({
  type: 'POST',
  data: {
   'csrfmiddlewaretoken': csrf,
   'myTag': myTag,
  },
  dataType: "json",
  url: url,
  }).done(function (data) {
        for (obj in data.mylist) {
            const mlist = data.mylist[obj]
            var content = '';
            content += '<option value=' + mlist.id + '>'+mlist.name+ '</option>';

            $('#id_area1').append(content);
        }
})
}



SaveAddGs.addEventListener('click', e => {

    e.preventDefault();
    var $this = $(this);
    let url = '/SaveAddGs/'
    let gsidGs = document.getElementById('gsidgs').value
    let nameGs = document.getElementById('namegs').value
    let addressGs = document.getElementById('addressgs').value
    let tellGs = document.getElementById('tellgs').value
    let master = document.getElementById('Master').value
    let id_area = document.getElementById('id_area1').value


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
 });


function getNazel(val) {
    document.getElementById('IdGs').value=val;
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

        var content ='';
        content += '<tr id="idn">'+ mlist.id + '</td>';
        content += '<td id="number">' + mlist.number + '</td>';
        content += '<td id="product">'+mlist.product+'</td>';
              content += '<td id="master">' + mlist.master + '</td>';
        content += '<td id="pinpad">'+mlist.pinpad+'</td>';

        content += '<td id="pumpbrand">'+mlist.pumpbrand+'</td>';
        content += '<td id="active">'+mlist.active+'</td>';
        content += '<td>'
        content += '<button id="editNazel" onclick="editNazelrow('+ mlist.id +')" class="btn nav-link bg-warning-bright" title=" ویرایش اطلاعات نازل" data-toggle="modal"\n' +
            '                               data-target="#editNazelmodal">\n' +
            '                                <i data-feather="edit" aria-hidden="true"></i>ویرایش\n' +
            '                            </button>';
        content += '</td>'


         $('#tblListNazel tbody').append(content);
          }
}
 });
}
function editNazelrow(val) {

}

SaveNazelAdd.addEventListener('click', e => {
    e.preventDefault();
    var $this = $(this);
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
                 content += '<td>'
                 content += '<button id="editNazel" onclick="editNazelrow(' + mlist.id + ')" class="btn nav-link bg-warning-bright" title=" ویرایش اطلاعات نازل" data-toggle="modal"\n' +
                     '                               data-target="#editNazelmodal">\n' +
                     '                                <i data-feather="edit" aria-hidden="true"></i>ویرایش\n' +
                     '                            </button>';
                 content += '</td>'


                 $('#tblListNazel tbody').append(content);
                  alarm('success','عملیات موفق ، نازل به درستی ایجاد شد')
             }else {
                 alarm('warning','عملیات ناموفق ، نازل تکراری است')
             }
         })
    });

Mylad.addEventListener('click', e => {

})