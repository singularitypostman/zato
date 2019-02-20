$(document).ready(function() {

    $.fn.zato.account.basic_settings.set_totp_key_qr_code();

    $('input[id^="color_"]').each(function(idx, input) {
        $(input).ColorPicker({
            color: '#0000ff',
            onShow: function(picker) {
                $(picker).fadeIn(100);
                return false;
            },
            onHide: function(picker) {
                $(picker).fadeOut(100);
                var id = $(input).attr('id').replace('color_', '');
                var span = $('#color_picker_span_' + id);

                $('#previev_a_'+id).remove();
                span.append(String.format('<a id="previev_a_{0}" href="javascript:$.fn.zato.account.basic_settings.preview({0})">(preview)</a>', id));
                return false;
            },
            onChange: function(hsb, hex, rgb) {
                _.each(['color', 'backgroundColor'], function(attr_name) {
                    _.each([input, '#cluster_color_div'], function(elem) {
                        $(elem).css(attr_name, '#' + hex);
                        $(elem).val(hex); // Works on the 'input' element only
                    });
                });
            }
        });
    });

    $('input[id^="checkbox_"]').change(function(e) {
        var id = $(this).attr('id').replace('checkbox_', '');
        var span = $('#color_picker_span_' + id);
        if(this.checked) {
            span.removeClass('hidden').addClass('visible');
        }
        else {
            span.removeClass('visible').addClass('hidden');
        };
    });

});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.account.basic_settings.preview = function(id) {
    var div = $('#cluster_color_div');
    div.removeClass('hidden').addClass('visible');
    div.css('backgroundColor', $('#color_'+id).css('backgroundColor'));
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


$.fn.zato.account.basic_settings.set_totp_key_qr_code = function() {

    var qr_code = new QRCode(document.getElementById('totp_key_qr_code'), {
        width : 100,
        height : 100
    });

    var token_elem = document.getElementById('id_totp_key');
    qr_code.makeCode(token_elem.value);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
