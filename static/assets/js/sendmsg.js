function msgFunction(val) {
var content=`

<div class="modal fade" id="msgmodal" tabindex="-1" role="dialog" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="exampleModalCenterTitle">ارسال پیام به : <input disabled style="border: none" id="idcodemeli" value=""></h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <i class="ti-close" aria-hidden="true"></i>
                    </button>
                </div>
                <div class="modal-body">
                   <div class="form-group">
<input id="subject_msg" class="form-control" type="text" value="" placeholder="موضوع پیام">
</div>
<div class="form-group">
<textarea id="info_msg" class="form-control" placeholder="شرح پیام"></textarea>
</div>


                    </input>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">بستن</button>
                    <button onclick="sendmsgmodal()" type="button" class="btn btn-primary"
                            data-dismiss="modal">ارسال پیام 
                    </button>
                </div>
            </div>
        </div>
    </div>


`

document.getElementById("msgDialog").innerHTML =content;
document.getElementById("idcodemeli").value =val

}

function sendmsgmodal(){

     $.ajax({
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
                'subject_msg': document.getElementById("subject_msg").value,
                'info_msg': document.getElementById("info_msg").value,
                'idcodemeli': document.getElementById("idcodemeli").value,

            },
            url: '/msg/msgmodal/',
            dataType: "json",
            success: function (resp) {
                if (resp.message === "success") {
                            alarm('info','پیام با موفقیت ارسال شد')
                    // }
                }
            }
        })
}