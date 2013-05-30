function popitup(url, name, height, width) {
    // http://www.quirksmode.org/js/popup.html
    height=height||600;
    width=width||800;

	newwindow=window.open(url,
                          name,
                          'resizable=yes,scrollbars=yes,height='+
                          height+',width='+width);
	if (window.focus) {newwindow.focus();}
	return false;
}

function ispopup(){
    return window.opener == null;
    //return (window.location.href == window.opener.location.href);
}

(function($){
    $(document).ready(function(){
                          if( window.opener == null  ){
                              $('.btn-image-path').attr('disabled', 'disabled');
                          }
                          else{
                              if($('.btn-image-path').length>0){
                                  $('.btn-image-path').click(function(){
                                 if (!ispopup) return false;
                                   window.opener.django.jQuery('#'+window.name)
                                    .val($(this).attr('data-image-path'));

                                   window.opener.django.jQuery('#img_'+window.name)
                                    .attr('src',$(this).attr('data-image-thumb'));

                                   window.opener.django.jQuery('#thumb_'+window.name)
                                    .show();

                                   window.close();
                              });
                            }

                            if($('.btn-select-image').length>0){
                                $('.btn-select-image').click(function(){
                                var popup_url = $(this).attr('data-popup-url');
                                var popup_name = $(this).attr('data-related-field');
                                popitup(popup_url,popup_name);
                                });
                            }
                          }
    });
})(django.jQuery);