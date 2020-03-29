$(document).ready(function() {
    $('a[href="' + location.pathname + '"]').closest('li').addClass('active');
    $('[data-toggle="tooltip"]').tooltip();
    $('.section-link').append((index) => {
        return '<a class="section-link-anchor" href="#' + $($('.section-link')[index]).attr('id') + '"> #</a>';
    });
    $('.is-invalid + *').addClass('is-invalid');
});