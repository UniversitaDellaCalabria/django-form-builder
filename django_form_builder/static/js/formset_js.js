/**
 * Create a new form using a template
 * @param  {HTML} formset_template: the default HTML schema to fill
 * @param  {String} prefix: the Django formset prefix
 * @param  {div} position:
 * @param  {String} generic_id:
 * @return false
 */
function clone(formset_template, prefix, position, generic_id) {
    // get total forms number in formset
    total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    // build the Regular Expression to replace generic elements
    var prefix_regex = new RegExp('('+prefix+'-'+generic_id+')', 'g')
    // generate new HTML block with "prefix+total indexed" form
    newElement = $(formset_template).html().replace(prefix_regex,
                                                    prefix+'-'+total);
    // place the new form before the "add new" button
    $(position).before(newElement);
    // increase total forms number in formset
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    // return false
    return false;
}

/**
 * Update the ID indexes of a form input fields
 * @param  {element} parent_div: the element that contains the form
 * @param  {String} prefix: the Django formset prefix
 * @return false
 */
function reindex_forms(parent_div, prefix){
    // build a Regular Expression to find all "form-INDEX" elements
    var id_regex = new RegExp('(' + prefix + ')-(\\d+)','g');
    // get the inner HTML of parent_div
    var parent_html = parent_div.html()
    // find the form in the HTML code
    var target = parent_html.match(id_regex);
    // get the INDEX value (es: form-1 -> 1)
    var splitted = target[0].split('-');
    var index = splitted[splitted.length-1];
    // decrease the index (es: form-1 -> form-0)
    var new_html = parent_html.replace(id_regex,
                                       prefix+'-'+(parseInt(index)-1));
    // update the parent_div HTML code
    parent_div.html(new_html);
    // return false
    return false;
}

/**
 * Delete the form and update the ID indexes of successive forms
 * @param  {element} to_remove: the element that contains the "remove" button and the form
 * @param  {String} prefix: the Django formset prefix
 * @param  {String} container_class_div: the class of div that contains the form
 */
function deleteForm(to_remove, prefix, container_class_div) {
    // calculate the number of total forms in formset
    total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    // retrieve all the forms following the one I'm deleting
    var successive_forms = to_remove.nextAll(container_class_div);
    // reindex each of them
    successive_forms.each(function(){
        reindex_forms($(this), prefix);
    });
    // remove the form
    to_remove.remove();
    // decrease total number
    total--;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
}

// "add new form" event using the generic form template
$(document).on('click', '.add-form-row', function(e){
    // If this method is called, the default action of the event will not be triggered.
    e.preventDefault();
    // get formset prefix
    var formset_prefix = $(this).attr('id').split(/add-form-(.+)/)[1]
    // get formset template
    var formset_template = $('#formset-template-'+formset_prefix);
    // get generic_id attribute
    var generic_id = formset_template.attr('generic_id')
    // get the position of "add new" button
    var position = $(this).parent();
    // clone the template and create a new form in formset
    clone(formset_template, formset_prefix, position, generic_id);
    // return false
    return false;
});

// "remove form" event
$(document).on('click', '.remove-form-row', function(e){
    // If this method is called, the default action of the event will not be triggered.
    e.preventDefault();
    // get the CSS class of element that contains form and button
    var container_class = '.form-container';
    // get formset prefix
    var prefix = $(this).attr('id').split(/-[0-9+]/)[0]
    // get the element to remove (contains the form and the "remove" button)
    var to_remove = $(this).closest(container_class);
    // call deleteForm method
    deleteForm(to_remove, prefix, container_class);
    // return false
    return false;
});
