function convertToFaToEn() {
            var tstr = document.forms[0].txtFa.value;

            var bstr = '';
            for (i = 0; i < tstr.length; i++) {
                if (tstr.charAt(i) >= '۰' && tstr.charAt(i) <= '۹') {
                    bstr += String.fromCharCode(tstr.charCodeAt(i) - 1728);
                }
                else {
                    bstr += tstr.charAt(i);
                }
            }

            document.forms[0].txtEn.value = bstr;
        }