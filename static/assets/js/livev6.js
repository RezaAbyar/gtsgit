// function Live_Info() {
//  // waiting();
//     $.ajax({
//         type: 'GET',
//         data: {},
//         url: '/api/get-live-info/',
//         dataType: "json",
//         }).done(function (resp) {
//         if (resp.message === "success") {
//
//             document.getElementById('openticket').innerText = resp.openticket
//             document.getElementById('count_me').innerText = resp.count_me
//             document.getElementById('openticketyesterday').innerText = resp.openticketyesterday
//             // }
//             // ending();
//         }
//     })
//        .fail(function (xhr, status, error) {
//             ending(1,error);
//         });
// }
//
// function Live_Info_Setad() {
//
//     $.ajax({
//         type: 'GET',
//         data: {},
//         url: '/api/get-live-info/',
//         dataType: "json",
//          }).done(function (resp) {
//         if (resp.message === "success") {
//              if (document.getElementById('openticket')){
//                 document.getElementById('openticket').innerText = resp.openticket
//              }
//             if (document.getElementById('closeticket')) {
//                 document.getElementById('closeticket').innerText = resp.closeticket
//             }
//                 if (document.getElementById('openticketyesterday')) {
//                     document.getElementById('openticketyesterday').innerText = resp.openticketyesterday
//                 }
//                     if (document.getElementById('nosell')) {
//                         document.getElementById('nosell').innerText = resp.nosell
//                     }
//                         if (document.getElementById('napaydar_today')) {
//                             document.getElementById('napaydar_today').innerText = resp.napaydari_today
//                         }
//                             if (document.getElementById('napaydar')) {
//                                 document.getElementById('napaydar').innerText = resp.napaydari
//                             }
//                                 // if (document.getElementById('counttest')) {
//                                 //     document.getElementById('counttest').innerText = resp.count_test +  <span><small>تیکت</small></span>
//                                 // }
//                                 //     if (document.getElementById('countfani')) {
//                                 //         document.getElementById('countfani').innerText = resp.count_fani +  <span><small>تیکت</small></span>
//                                 //     }
//                                 //         if (document.getElementById('counttek')) {
//                                 //             document.getElementById('counttek').innerText = resp.count_tek +  <span><small>تیکت</small></span>
//                                 //         }
//                                 //             if (document.getElementById('countengin')) {
//                                 //                 document.getElementById('countengin').innerText = resp.count_engin +  <span><small>تیکت</small></span>
//                                 //             }
//
// if (document.getElementById('rpm')) {
//     document.getElementById('rpm').innerText = resp.rpm
// }
// chartrow(8)
//  $('#listticket').empty()
//
//
//                 for (obj in resp.count_failure) {
//                     const mlist = resp.count_failure[obj]
// var content = '';
//                     content += '<div class="col-md-3"><div class="card"><table><thead> <tr> <th style="font-size: 15px">'+mlist.name+'</th></tr></thead>'
//                     content += '<tbody><tr><td style="font-size: 80px" class=" text-center font-weight-bold text-warning">'+mlist.tedad+'</td></tr></tbody></table>'
//                     $('#listticket').append(content);
//                 }
//
//
//             // }
//         }
//     })
//               .fail(function (xhr, status, error) {
//             ending(1,error);
//         });
// }
//
// function Live_Info_Bohran() {
//  waiting();
//     $.ajax({
//         type: 'GET',
//         data: {},
//         url: '/api/get-live-bohran/',
//         dataType: "json",
//          }).done(function (resp) {
//
//              if (document.getElementById('ok_init_id')){
//                 document.getElementById('ok_init_id').innerText = resp.ok_init
//              }
//             if (document.getElementById('no_init_id')) {
//                 document.getElementById('no_init_id').innerText = resp.no_init
//             }
//                       if (document.getElementById('err_init_id')) {
//                 document.getElementById('err_init_id').innerText = resp.err_init
//             }
//                 if (document.getElementById('sum_id')) {
//                     document.getElementById('sum_id').innerText = resp.sums
//                 }
//
//  $('#myTable tbody').empty()
//                 for (obj in resp.mlist) {
//                     const mlist = resp.mlist[obj]
//                     var content = '';
//                     content += '<tr id="' + mlist.zone + '">';
//                     content += '<td class="text-center">' + mlist.zone + '</a></td>'
//                     content += ' <td class="text-center"><a href="ClosedTickets/?select=&select2=&zone=' + mlist.zoneid +'&organization=2&failure=1171&failure=1172&gsid=">' + mlist.ok_int + '</td>'
//                     content += ' <td class="text-center"><a href="CrudeTickets/?select=&select2=&zone=' + mlist.zoneid +'&organization=2&failure=1172&gsid=">' + mlist.no_int + '</td>'
//                     content += ' <td class="text-center"><a href="CrudeTickets/?select=&select2=&zone=' + mlist.zoneid +'&organization=1&failure=1172&gsid="> ' + mlist.err_int + '</td>'
//                     $('#myTable tbody').append(content);
//
//                 }
//
//   ending();
//             // }
//
//     })
//               .fail(function (xhr, status, error) {
//             ending();
//         });
// }

