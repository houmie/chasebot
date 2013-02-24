/*jslint plusplus: true, browser: true, devel: true */
/*global $, jQuery, gettext, Modernizr, BigDecimal, BigInteger, RoundingMode, confirm, add_deal_to_formset, add_deal_to_formset, row_edit_ajax, reload_edit_save_cancel_buttons, rebind_conversations, rebind_sales_item, rebind_events, rebind_open_deals, rebind_deal_templates, bind_main_tabs, rebind_contacts*/

var isVisible = false;
var clickedAway = false;

function getCookie(name) {
    "use strict";
    var cookieValue, cookies, i, cookie;
    cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        cookies = document.cookie.split(';');
        for (i = 0; i < cookies.length; i++) {
            cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    "use strict";
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function (xhr, settings) {
        "use strict";
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

 /*, 0..n args */
function partial(func) {
    "use strict";
    var args = Array.prototype.slice.call(arguments, 1);
    return function () {
        var allArguments = args.concat(Array.prototype.slice.call(arguments));
        return func.apply(this, allArguments);
    };
}


if (!String.prototype.trim) {
   //code for trim
    String.prototype.trim = function () {
        "use strict";
        return this.replace(/^\s+|\s+$/g, '');
    };
}

function draggable_modal(modal_id) {
    "use strict";
    $(modal_id).draggable({
        handle: ".modal-header"
    });
}

$(function () {
    "use strict";
    $.extend($.tablesorter.themes.bootstrap, {
    // these classes are added to the table. To see other table classes available, 
    // look here: http://twitter.github.com/bootstrap/base-css.html#tables 
        table: 'table',
        header: 'bootstrap-header', // give the header a gradient background 
        footerRow: '',
        footerCells: '',
        icons: '', // add "icon-white" to make them white; this icon class is added to the <i> in the header 
        sortNone: 'bootstrap-icon-unsorted',
        sortAsc: 'icon-chevron-up',
        sortDesc: 'icon-chevron-down',
        active: '', // applied when column is sorted 
        hover: '', // use custom css here - bootstrap class may not override it 
        filterRow: '', // filter row class 
        even: '', // odd row zebra striping 
        odd: '' // even row zebra striping 
    });
});

function cloneMore(selector, type, row) {
    "use strict";
    var empty_X, total;
    //Selector is in this case the node to clone from (empty extra form in a separate section in the DOM tree)
    empty_X = $(selector).clone(true);
    //Total is teh number of available tabs (deals)
    total = $(row).find('#attached_deals_tab li').length;

    //Rename each extra_deal-0- occurance of the cloned element to deals-total-, whatever total is currently     
    empty_X.find(':input').each(function () {
        var name, id;
        name = $(this).attr('name').replace('extra_deal-0-', type + '-' + total + '-');
        id = 'id_' + name;
        $(this).attr({'name': name, 'id': id});
    });
    empty_X.find('label').each(function () {
        var newFor = $(this).attr('for').replace('extra_deal-0-', type + '-' + total + '-');
        $(this).attr('for', newFor);
    });
    return empty_X;
}

function run(opts) {
    "use strict";
    var bd, result, ops, a, b, op;
    bd = {"BigDecimal": BigDecimal, "BigInteger": BigInteger, "RoundingMode": RoundingMode};
    ops = {'*': "multiply", '/': "divide", '+': "add", '-': "subtract"};
    a = new bd.BigDecimal(opts.a.toString());
    b = new bd.BigDecimal(opts.b.toString());
    op = ops[opts.op];
    if (op === "divide") {
        return a.divide(b, 300, bd.RoundingMode.HALF_UP());
    }
    return a[op].call(a, b);
}

function multiply(a, b) {
    "use strict";
    return run({"a": a, "b": b, "op": "*"});
}

function rebind_attach_deals(parent, row) {
    "use strict";
    var total, i, total_value, total_node, a, b;
    //Upon opening make sure that all deals from attached_deal_formset will get chosenified. 
    // Attention: Do NOT chosenify the extra-deal form, or it would break.  
    total = $(row).find('#id_deals-TOTAL_FORMS').val();
    for (i = 0; i <= total; i++) {
        $(parent).find('#id_deals-' + i + '-sales_item').chosen({no_results_text: gettext('No results match')});
        a = $(parent).find('#id_deals-' + i +  '-price').val();
        b = $(parent).find('#id_deals-' + i +  '-quantity').val();
        if (a && b) {
            total_value = multiply(a, b);
            total_node = $(parent).find('#id_deals-' + i +  '-total_value');
            if (total_node) {
                total_node.val(total_value);
            }
        }
    }
}

function calc_totals() {
    "use strict";
    var total_value = multiply($('#deal_modal_body').find('.quantity').val(), $('#deal_modal_body').find('.price').val());
    $('#deal_modal_body').find('.total_value').val(total_value);
}

function calc_total_value() {
    "use strict";
    $('#deal_modal_body').find('.quantity').off('change').on('change', calc_totals);
    $('#deal_modal_body').find('.price').off('change').on('change', calc_totals);
}

function mark_tab_header_error(form, element, is_error) {
    "use strict";
    var id = $(form).find(element).closest('.tab-pane').attr('id');
    $(form).find(element).closest('.tabbable').find('.tab_header').each(function (index, value) {
        if ($(this).attr('href') === '#' + id) {
            if (is_error) {
                $(this).css({color: 'red'});
            } else {
                $(this).removeAttr('style');
            }
        }
    });
}

function validation_rules(form) {
    "use strict";
    var validator = $(form).validate({
            // options
            onkeyup: function (element) {
                $(element).valid();
                if (validator.numberOfInvalids() > 0) {
                    mark_tab_header_error(form, validator.lastElement, true);
                }
            },
            errorPlacement: function (error, element) {
                var field_error = $(form).find('#id_' + element.attr('name')).siblings('.field_error');
                if (field_error.length > 0) {
                    error.appendTo(field_error);
                } else {
                    field_error = $(form).find('#id_' + element.attr('name')).closest('td').children('.field_error');
                    error.appendTo(field_error);
                }
                $(field_error).show();
            },
            // ignore: ':hidden:not(.chzn-done)'
            ignore: "",
            invalidHandler: function () {
                $("#validation_summary").text(validator.numberOfInvalids() + gettext(" field(s) are invalid"));
            },
            errorContainer: "#validation_summary",
            success: function () {
                mark_tab_header_error(form, validator.lastElement, false);
            }
        });

    $(form).find('select.mandatory').each(function () {
        $(this).change(function () {
            $(this).valid();
        });
        $(this).rules('add', {
            valueNotEquals: ""
        });
    });

    $(form).find('select.multi_select_mandatory').each(function () {
        $(this).chosen().change(function () {
            $(this).valid();
        });
        $(this).rules('add', {
            required: true
        });
    });
    return validator;
}

function show_modal(target, custom_width) {
    "use strict";
    var width;
    if (custom_width) {
        width = custom_width;
    } else {
        width = 'auto';
    }

    $(target).modal({
        backdrop: true,
        keyboard: true
    }).css({
        width: width,
        'margin-left': function () {
            return -($(this).width() / 2);
        }
    });

    $(target).modal('show');
}

function create_btn_deals(row) {
    "use strict";
    //For each tab on attached deals tab control we create one button 
    $(row).find('#clipped_deals').empty();
    $(row).find('#attached_deals_tab li a').each(function () {
        var btn, span;
        btn = $('<a/>', {'class': 'btn btn-small', href: $(this).attr('href')});
        span = $('<span/>', { 'class': 'badge badge-info', text: $(this).text()}).appendTo(btn);
        $(row).find('#clipped_deals').append(btn);

        btn.click(function (event) {
            event.preventDefault();
            var cloned_tab_div, form, total, validator;
            //The btn's href is the same as its tab pendant's href, which in turn points to the tab content.
            //Hence we clone the content of the tab within the loaded row only.
            cloned_tab_div = $(row).find(btn.attr('href')).children().clone();
            $('#deal_modal_body').empty();
            //Form is only required for validation, but it doesn't submit
            form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'}).append(cloned_tab_div);
            $('#deal_modal_body').append(form);

            total = $(row).find('#attached_deals_tab li').length;
            validator = validation_rules('#deal_modal_form');

            $('#deal_modal_confirm_btn').off('click').on('click', {validator: validator, btn: btn}, function (event) {
                event.preventDefault();
                var validator, source, target;
                validator = event.data.validator;
                if (validator.numberOfInvalids() === 0) {
                    source = $('#deal_modal_body').children('form').children('div').clone();
                    target = $(row).find('#tab-content').find($(btn).attr('href'));
                    target.empty();
                    target.append($(source));
                    $('#deal_modal').modal('hide');
                    create_btn_deals(row);
                }
            });

            rebind_attach_deals('#deal_modal_body', row); //TODO: Recheck later
            calc_total_value();
            $('#deal_modal').find('#modal_h3').text(gettext('Edit Deal'));
            $('#delete_deal_table').removeClass('hidden');
            show_modal('#deal_modal');
        });
    });
}

function fill_emptyX_with_predefined_or_existing_data(selected_id, type, empty_X, path, row, contact_id) {
    "use strict";
    var url = '';

    //If contact_id is provided it means that we are dealing with an open deal, since we need to open the existing open instance for further processing
    if (contact_id) {
        url = path + selected_id + '/' + contact_id;
    } else { //otherwise we are adding a new deal
        url = path + selected_id + '/';
    }

    //Here we make an ajax call to the server to get the data from the selected deal Template or get the data from the last open deal instance,
    //In either case the user can then override these values  
    $.ajax({
        type: 'GET',
        url: url,
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (data) {
            var total, template_name, deal_instance_name, vals, i, validator;
            total = $(row).find('#attached_deals_tab li').length;
            template_name = '';
            deal_instance_name = '';

            if (contact_id) {
                //if contact_id is provided it means we are dealing with open deal
                //the returned json object will be from a deal object, therefore we check against deal specific fields
                template_name = data[0].fields.deal_template_name;
                deal_instance_name = data[0].fields.deal_instance_name;
            } else {
                //otherwise we are adding a new deal and the returned json object will be a deal_template object, and therefore we need to check against deal_template specific fields
                template_name = data[0].fields.deal_name;
            }

            // Set all the values from json into the cloned fields accordingly
            //Attention, when setting ANY field to the value from json follow these rules: 
            // Set the value for all inputs with .attr('value', foo)
            // Set the value for all dropdowns with val() so that the primary key is used.
            // for m2m you need to use val() on an array (see below)

            empty_X.find('#id_deals-' + total + '-deal_template_name').attr('value', template_name);
            empty_X.find('#id_deals-' + total + '-deal_instance_name').attr('value', deal_instance_name);

            //empty_X.find('#id_deals-' + total + '-deal_description').attr('value', data[0].fields['deal_description']);
            empty_X.find('#id_deals-' + total + '-deal_description').text(data[0].fields.deal_description);
            empty_X.find('#id_deals-' + total + '-sales_term').val(data[0].fields.sales_term);
            empty_X.find('#id_deals-' + total + '-price').attr('value', data[0].fields.price);
            empty_X.find('#id_deals-' + total + '-currency').val(data[0].fields.currency);
            empty_X.find('#id_deals-' + total + '-quantity').attr('value', data[0].fields.quantity);

            if (data[0].fields.hasOwnProperty('status')) {
                empty_X.find('#id_deals-' + total + '-status').val(data[0].fields.status);
            } else {
                empty_X.find('#id_deals-' + total + '-status>option:eq(1)').prop('selected', true);
            }

            if (data[0].fields.hasOwnProperty('deal_template')) {
                empty_X.find('#id_deals-' + total + '-deal_template').val(data[0].fields.deal_template);
            } else {
                empty_X.find('#id_deals-' + total + '-deal_template').val(data[0].pk);
            }

            //m2m needs special treatment with arrays
            vals = [];
            for (i = 0; i <= data[0].fields.sales_item.length; i++) {
                vals.push(data[0].fields.sales_item[i]);
            }
            empty_X.find('#id_deals-' + total + '-sales_item').val(vals);

            if (contact_id) {
                //Open deal                
                //We need to populate the open_deal_id that was selected from dropdown into a hidden field. This will be later used in request.POST on server
                // to load the former open deal instance 
                //TODO: Maybe we could pass UUID of the deal and the set by json, so that we don't have to load the open_deal again in request.POST'
                empty_X.find('#id_deals-' + total + '-attached_open_deal_id').attr('value', selected_id);
            }
            $('#deal_modal_body').children('form').append(empty_X);
            rebind_attach_deals('#deal_modal_body', row);
            calc_total_value();
            calc_totals();
            validator = validation_rules('#deal_modal_form');
            $('#deal_modal').find('#deal_modal_confirm_btn').off('click').on('click', {row: row, validator: validator}, add_deal_to_formset);
            $('#deal_modal').find('#deal_modal_confirm_btn').show();
        }
    });
}

function add_deals(event) {
    "use strict";
    //Adding new deals
    event.preventDefault();
    var row, type, empty_X, selected_id;
    row = $(event.data.row);
    type = 'deals';
    empty_X = cloneMore('#X div:first', type, row);

    //Getting the deal Template id from the selected dropdown
    selected_id = $('#deal_modal_body').find('.pre_defined_deal_dropdown option:selected').val();
    if (selected_id) {
        fill_emptyX_with_predefined_or_existing_data(selected_id, type, empty_X, '/deal_template/', row);
    }
    $(event.currentTarget).parent().parent().parent().remove();
}

function add_opendeals(event) {
    "use strict";
    //Adding an open deal
    event.preventDefault();
    var row, type, empty_X, selected_id, contact_id;
    row = $(event.data.row);
    type = 'deals';
    empty_X = cloneMore('#X div:first', type, row);

    //Getting the open deal instance id from the selected dropdown
    selected_id = $('#deal_modal_body').find('#id_opendeals_add_form-open_deal_template option:selected').val();
    contact_id = $('#deal_modal_body').find('#contact_id').text();
    if (selected_id) {
        fill_emptyX_with_predefined_or_existing_data(selected_id, type, empty_X, '/open_deal/', row, contact_id);
    }
    event.currenTarget.parent().parent().parent().remove();
}

function bind_attach_deal(row) {
    "use strict";
    $(row).find('#add_deal_template').click(function (event) {
        event.preventDefault();
        var dropdown, form;
        dropdown = $(row).find('#add_deals_dropdown div:first').clone();
        $('#deal_modal_body').empty();
        form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'}).append(dropdown);
        $('#deal_modal_body').append(form);
        $('#deal_modal_body').find('#add_deals_button').off('click').on('click', {row: row}, add_deals);
        $('#deal_modal').find('#deal_modal_confirm_btn').hide();
        $('#deal_modal').find('#modal_h3').text(gettext('Add New Deal From Template'));
        show_modal('#deal_modal');
    });

    $(row).find('#continue_deal').click(function (event) {
        event.preventDefault();
        var dropdown, form;
        dropdown = $(row).find('#add_opendeals_dropdown div:first').clone();
        $('#deal_modal_body').empty();
        form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'}).append(dropdown);
        $('#deal_modal_body').append(form);
        $('#deal_modal_body').find('#add_opendeals_button').off('click').on('click', {row: row}, add_opendeals);
        $('#deal_modal').find('#deal_modal_confirm_btn').hide();
        $('#deal_modal').find('#modal_h3').text(gettext('Continue With Existing Deal'));
        show_modal('#deal_modal');
    });

    $(row).find('#new_deal').click(function (event) {
        event.preventDefault();
        $('#deal_modal_body').empty();
        var form, type, empty_X, validator;
        form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'});
        $('#deal_modal_body').append(form);

        //Adding new deals  
        type = 'deals';
        empty_X = cloneMore('#X div:first', type, row);
        $('#deal_modal_body').children('form').append(empty_X);
        rebind_attach_deals('#deal_modal_body', row);
        calc_total_value();

        $('#deal_modal_body').find('.deal_status').val(1);
        validator = validation_rules('#deal_modal_form');
        $('#deal_modal').find('#deal_modal_confirm_btn').off('click').on('click', {row: row, validator: validator}, add_deal_to_formset);
        $('#deal_modal').find('#deal_modal_confirm_btn').show();
        $('#deal_modal').find('#modal_h3').text(gettext('Create Your Own Deal'));
        show_modal('#deal_modal');
    });
}

function add_deal_to_formset(event) {
    "use strict";
    event.preventDefault();
    var validator, row, total, newname, slug, a, li, div, source;
    validator = event.data.validator;

    validator.form();
    if (validator.invalidElements().length > 0) {
        return;
    }

    row = $(event.data.row);
    total = $(row).find('#attached_deals_tab li').length;
    newname = $('#deal_modal_body').find('#id_deals-' + total + '-deal_instance_name').val();

    //The newname either template_name or instance_name will be stripped from spaces and dots and replaced with _. So that its compatible for URL id's
    slug =  newname.replace(/ /g, "_").replace(/\./g, "_");
    //Now that the copying of json into the cloned fields is over we create the tabs                        
    a = document.createElement('a');
    a.setAttribute('data-toggle', 'tab');
    a.setAttribute('href', '#' + slug);
    a.innerHTML = newname;

    li = document.createElement('li');
    li.appendChild(a);

    //Attaching the tab header
    $(row).find('#attached_deals_tab').append(li);

    //creating the tab content
    div = document.createElement('div');
    div.setAttribute('class', 'tab-pane');

    //Setting the id of tab content to the same url href of tab header, so that it can be found when user clicks on the tab header
    div.setAttribute('id', slug);

    source = null;
    if ($('#deal_modal_body').children('form').children('div').length === 1) {
        source = $('#deal_modal_body').children('form').children('div');
    } else {
        source = $('#deal_modal_body').children('form').children('div').eq(1);
    }

    //attaching the cloned element with json values to the tab content 
    $(div).append($(source));
    $(row).find('#tab-content').append(div);

    //TODO: Perhaps obsolete. We should add as many deals, even if not closed. remove item by chosen instead ?    
    //In case of adding a new deal we need to remove the selected deal Template from the dropdown, so it can't be added again to the same call.
    //$(row).find("#id_deals_add_form-deal_template option[value='" + selected_id + "']").remove();    

    //Finally set the total form value within the formset to the number of added tabs, so that it can be saved in request.POST 
    total = $(row).find('#attached_deals_tab li').length;
    $(row).find('#id_deals-TOTAL_FORMS').attr('value', total);

    $('#deal_modal').modal('hide');
    create_btn_deals(row);
}

function sort_table(table, condition) {
    "use strict";
    $(table).bind("sortBegin", function (e, table) {
        if ($(condition).length > 0) {
            alert(gettext("Can't sort while a deal is expanded. Please collapse the open row first and try again."));
            throw new Error("Can't sort, while open deal row is openened.");
        }
    });
    // call the tablesorter plugin and apply the uitheme widget 
    $(table).tablesorter({
        theme: "bootstrap", // this will  
        headers: {
          // disable sorting of the first column (we start counting at zero) 
            0: {
            // disable it by setting the property sorter to false 
                sorter: false
            },
            1: { sorter: false },
            5: { sorter: "text" }
        },
        widthFixed: true,
        // textExtraction : {
            // 4: function(node) { return $(node).text(); },        
        // },
        headerTemplate: '{content} {icon}', // new in v2.7. Needed to add the bootstrap icon! 

        // widget code contained in the jquery.tablesorter.widgets.js file 
        // use the zebra stripe widget if you plan on hiding any rows (filter widget) 
        widgets: ["uitheme", "zebra"],

        widgetOptions: {
            // using the default zebra striping class name, so it actually isn't included in the theme variable above 
            // this is ONLY needed for bootstrap theming if you are using the filter widget, because rows are hidden 
            zebra: ["even", "odd"],

            // reset filters button 
            filter_reset: ".reset"

            // set the uitheme widget to use the bootstrap theme class names 
            // uitheme : "bootstrap" 
        },

        // called after each header cell is rendered, use index to target the column
        // customize header HTML
        onRenderHeader: function (index) {
            // the span wrapper is added by default
            $(this).find('div.tablesorter-header-inner').addClass('roundedCorners');
        },
        // prevent text selection in header
        cancelSelection: true

    }).tablesorterPager({
        // target the pager markup - see the HTML block below 
        container: $(".pager"),

        // target the pager page select dropdown - choose a page 
        cssGoto: ".pagenum",

        // remove rows from the table to speed up the sort of large tables. 
        // setting this to false, only hides the non-visible rows; needed if you plan to add/remove rows with the pager enabled. 
        removeRows: false,

        // if true, the table will remain the same height no matter how many
        // records are displayed. The space is made up by an empty 
        // table row set to a height to compensate; default is false 
        fixedHeight: true,

        // output string - default is '{page}/{totalPages}'; 
        // possible variables: {page}, {totalPages}, {filteredPages}, {startRow}, {endRow}, {filteredRows} and {totalRows} 
        output: '{startRow} - {endRow} ({totalRows})',

        //ajaxUrl : "/open_deals/?page={page}&size={size}",

        page: 0,

        size: 10,

        // ajaxProcessing: function (data) {
            // if (data) {
                // var i, rows, totals, r, row, c, headers, rw;
                // rows = [];
                // totals = data.total_rows;
                // headers = data.cols;
                // for (r = 0; r < data.rows.length; r++) {
                    // row = []; // new row array                    
                    // // cells
                    // for (i = 0; i < headers.length; i++) {
                        // c = data.rows[r][headers[i]];
                        // if (typeof (c) === "string") {
                            // row.push(c); // add each table cell data to row array
                        // }
                    // }
                    // rows.push(row); // add new row array to rows array
                // }
// 
                // return [ totals, rows, headers ];
            // }
        // },

        // css class names of pager arrows
        cssNext        : '.next',  // next page arrow
        cssPrev        : '.prev',  // previous page arrow
        cssFirst       : '.first', // go to first page arrow
        cssLast        : '.last',  // go to last page arrow
        cssPageDisplay : '.pagedisplay', // location of where the "output" is displayed
        cssPageSize    : '.pagesize', // page size selector - select dropdown that sets the "size" option
        cssErrorRow    : 'tablesorter-errorRow', // error information row

        // class added to arrows when at the extremes (i.e. prev/first arrows are "disabled" when on the first page)
        cssDisabled    : 'disabled' // Note there is no period "." in front of this class name

    });
}

function row_delete_ajax(event) {
    "use strict";
    event.preventDefault();
    var target, rebind_func, url;
    target = $(event.data.target);
    rebind_func = event.data.rebind_func;
    if (confirm(gettext('Are you sure you want to delete this row?'))) {
        url = $(event.currentTarget).attr("href");
        $.post(url, function (result) {
            $(target).empty();
            $(target).append(result);
            rebind_func();
        });
    }
}

function filter_rows(event) {
    "use strict";
    event.preventDefault();
    var rebind_func, url;
    rebind_func = event.data.rebind_func;
    url = $(event.currentTarget).attr('action');

    // With ajax as first keywork we can check against in views.py and refresh the list if all filters are cleared but the request came by ajax
    url = url + '?ajax';

    //Check each input box for values and apply keyword search 
    $('.form-filter-ajax').find('input').each(function (i, v) {
        var keyword, value, values;

        //id_last_name -> last_name
        keyword = $(v).attr('id').substring(3);

        //Only if it contains any value in the field, attach it to the url GET, otherwise its pointless
        value = $(v).val();
        if (value !== '') {
            // if($(v).attr('type') == 'date'){
            // }            

            //If multiple parameters are passed seperated by commas...
            if (value.indexOf(',') !== -1) {
                values = value.split(',');
                $(values).each(function (i, v) {
                    if (v.trim() !== '') {
                        //Put each paramater in its own keyword .e.g. ?ajax&sales_item=t3&sales_item=t1
                        url = url + '&' + keyword + '=' + v.trim();
                    }
                });
            } else { //If single paramaters are passed in...
                url = url + '&' + keyword + '=' + encodeURIComponent(value);
            }
        }
    });
    //Even if no filter are set, still the query to server is required to get all list and undo filters.    
    $('#search_result').load(url, {rebind_func: rebind_func}, function () {
        rebind_func();
    });
}

function paginator_navigate(event) {
    "use strict";
    event.preventDefault();
    var url, target_pane, rebind_func;
    url = $(event.currentTarget).attr('href');
    target_pane = event.data.target_pane;
    rebind_func = event.data.rebind_func;

    //hack TODO
    if ($('#details').length > 0) {
        $('#details').remove();
        target_pane = "#search_result";
    }

    //If the page containing the paginator is a modal, then we need to know its type, to modify the url accordingly 
    //Otherwise the url would point to the page containing the modal.    
    $(target_pane).load(url, function (result) {
        rebind_func();
    });
}


function rebind_conversation_deal_btn(row) {
    "use strict";
    create_btn_deals(row);
    bind_attach_deal(row);
}

function rebind_edit_delete(source, rebind_func) {
    "use strict";
    $(source).find(".row_delete_ajax").off('click').on('click', {target: source, rebind_func: rebind_func}, row_delete_ajax);
    $(source).find(".row_edit_ajax").off('click').on('click', {source: source}, row_edit_ajax);
}

//Used by Conversation and Sales Items
function row_edit_save_ajax(event) {
    "use strict";
    event.preventDefault();
    var url, isNewConversation, source, row, data, ths;
    ths = event.currentTarget;
    url = event.data.url;
    isNewConversation = event.data.isNewConversation;
    source = event.data.source;

    row = $(ths).closest('tr');
    data = $(ths).closest('#save_edit_form').serialize();

    $.post(url, data, function (result) {
        //If there are validation errors upon editing the field
        if ($('#validation_error_ajax', result).text() === 'True') {
            //if so, then we empty the current row and load the invalid-indicating-forms in the row 
            //and attach events to the still existing save and cancel buttons
            row.empty();
            row.append(result);
            reload_edit_save_cancel_buttons($(row), url, false, source);
        } else {
            //if no error, then simply add the full 'tr' html row (with delete and edit icons) behind this row and remove this row. 
            var row_before = $(result).insertBefore(row);
            row.remove();
            rebind_edit_delete('#search_result', function () {
                rebind_conversations();
                rebind_sales_item(source);
            });
            rebind_conversations();
            rebind_sales_item(source);
            if (isNewConversation) {
                $('#new_conversation_button').button('toggle');
            }
        }
    });
}

function datepicker_reload(source, isPast) {
    "use strict";
    var options, is_showMeridian;
    options = { format: $('#locale').text(),
            weekStart: 1,
            autoclose: 'True',
            todayHighlight: 'True' };

    if (isPast) {
        options.endDate = $('#user_date').text();
    } else {
        options.startDate = $('#user_date').text();
    }

    if (Modernizr.touch && Modernizr.inputtypes.date) {
        $(source).find('.date_picker').type = 'date';
    } else {
        $(source).find('.date_picker').datepicker(options);
    }

    is_showMeridian = false;
    if ($('#locale').text() === 'mm/dd/yyyy') {
        is_showMeridian = true;
    }
    $(source).find('.timepicker-default').timepicker({showMeridian: is_showMeridian, defaultTime : false});
}

//Used by Conversation & Sales Items
function reload_edit_save_cancel_buttons(row, url, isNewConversation, source) {
    "use strict";
    $(row).find("#save_edit_form").submit({url: url, isNewConversation: isNewConversation, source: source}, row_edit_save_ajax);
    $(row).find("#save_edit_button").click(function () {
        $(row).find("#save_edit_form").submit();
    });
    if (isNewConversation) {
        $(row).find("#cancel_edit_button").off('click').on('click', function (event) {
            event.preventDefault();
            $(row).remove();
            $('#new_conversation_button').button('toggle');
        });
    } else {
        $(row).find("#cancel_edit_button").off('click').on('click', function (event) {
            event.preventDefault();
            var url, row;
            url = $(this).attr("href") + "/";
            row = $(this).closest('form').closest('tr'); //real row containing also the submit-edit-form    
            row.load(
                // get only the children (td) of the tr and attach them to the existing empty row.
                url + ' td',
                function () {
                    rebind_edit_delete($(row), function () {
                        // After Delete the row is gone, no need to bind anything after.
                    });
                }
            );
        });
    }
    datepicker_reload($(row), true);
}

//Currently used by Conversations & sales items
function row_edit_ajax(event) {
    "use strict";
    event.preventDefault();
    var source, url, row, ths;
    ths = event.currentTarget;
    source = event.data.source;
    // e.g. url = '/sales_item/edit/8' 
    url = $(ths).attr("href") + "/";
    //e.g. get whole row to be replaced with editing fields
    row = $(ths).closest('tr');
    row.load(url, function (result) {
            //Once loaded make sure the submit-form will be redirected to 'row_edit_save_ajax' once submitted. Url is parameter 
        reload_edit_save_cancel_buttons($(row), url, false, source);
        rebind_conversation_deal_btn($(row));
    });
}

function row_add_save_sales_item(event) {
    "use strict";
    event.preventDefault();
    var source, url, row, data;
    source = event.data.source;
    // selector starts from Add Button (this)   
    url = $('#save_add_form').attr('action');
    row = $(event.currentTarget).closest('tr'); //real row containing also the form    
    data = $("#save_add_form").serialize();

    $.post(url, data, function (result) {
        //If there are validation errors upon adding the field
        if ($('#validation_error_ajax', result).text() === 'True') {
            row.empty();
            row.append(result);
            rebind_sales_item(source);
        } else {
            //if there is no error then insert the added row before the current add-button row. (last row)          
            $(source).find('#search_result').empty();
            $(source).find('#search_result').append(result);
            rebind_sales_item(source);
            $(".item_name").val('');
        }
    });
}

//This function is kept very generic !
//the first two are internal parameters to make typeahead work.
//fieldname is the field to filter against.
//contact_id is the optional id that some querysets might need as prerequisite.
function autocomplete(query, process, path, fieldname, contact_id) {
    "use strict";
    var url = '';
    //If contact_id is passed in then we have a different url path to pass in the contact_id
    if (contact_id === '') {
        url = '/autocomplete/' + path + '/';
    } else {
        url = '/autocomplete/' + path + '/' + contact_id + '/';
    }

    //Pass in the query (typed keywords) and the fieldname we are searching against 
    $.ajax({
        type: 'GET',
        url: url,
        data: { query: query, fieldname: fieldname },
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (data) {
            return process(data);
        }
    });
}

//The average typeahead function passes in two parameters. First one is the category (which defines the related queryset) 
//and the second is the actual field to filter.
function typeahead_sales_items(query, process) {
    "use strict";
    autocomplete(query, process, 'sales_items', 'item_name', '');
}

function typeahead_contacts_last_name(query, process) {
    "use strict";
    autocomplete(query, process, 'contacts', 'last_name', '');
}

function typeahead_opendeal_deal_name(query, process) {
    "use strict";
    autocomplete(query, process, 'open_deals', 'deal_instance_name', '');
}

function typeahead_opendeal_status(query, process) {
    "use strict";
    autocomplete(query, process, 'open_deals', 'status', '');
}

function typeahead_opendeal_total_value(query, process) {
    "use strict";
    autocomplete(query, process, 'open_deals', 'total_value', '');
}

function typeahead_contacts_first_name(query, process) {
    "use strict";
    autocomplete(query, process, 'contacts', 'first_name', '');
}

function typeahead_contacts_company(query, process) {
    "use strict";
    autocomplete(query, process, 'contacts', 'company_name', '');
}

function typeahead_contacts_email(query, process) {
    "use strict";
    autocomplete(query, process, 'contacts', 'email', '');
}

//This method passes in three parameters, the last one is the contact_id. Since all calls must belong to a contact.
function typeahead_deals_deal_name(query, process) {
    "use strict";
    autocomplete(query, process, 'deal_template', 'deal_name', '');
}

function typeahead_deals_sales_item(query, process) {
    "use strict";
    autocomplete(query, process, 'deal_template', 'sales_item', '');
}

function typeahead_deals_price(query, process) {
    "use strict";
    autocomplete(query, process, 'deal_template', 'price', '');
}

function typeahead_deals_sales_term(query, process) {
    "use strict";
    autocomplete(query, process, 'deal_template', 'sales_term', '');
}

function typeahead_deals_quantity(query, process) {
    "use strict";
    autocomplete(query, process, 'deal_template', 'quantity', '');
}

function rebind_paginator(source, target, rebind_func) {
    "use strict";
    $(source).find(".paginator_nav_links").off('click').on('click', {target_pane: target, rebind_func: rebind_func}, paginator_navigate);
}

function rebind_task_edit_delete(parent) {
    "use strict";
    $(parent).find(".row_delete_ajax").off('click').on('click', {target: parent}, row_delete_ajax);
}

function rebind_delete_paginator(source, target, rebind_func) {
    "use strict";
    $(source).find(".row_delete_ajax").off('click').on('click', {target: target, rebind_func: rebind_func}, row_delete_ajax);
    var target_pane = $(source).find(target);
    $(source).find(".paginator_nav_links").off('click').on('click', {target_pane: target, rebind_func: rebind_func}, paginator_navigate);
}

// This rebinds all rating classes within the templates (not forms)
function rebind_ratings(parent) {
    "use strict";
    $(parent).find('.rating').each(function (i, v) {
        // The radio button template tag shows which button was selected from None, 1, 2, 3. The number is then taken to use as score.
        var selection = 0;
        if ($(v).text().trim() !== 'None') {
            selection = parseInt($(v).text().trim(), 10);
        }
        $(v).children('.star_small').raty({
            score     : selection,
            readOnly  : true,
            half      : false,
            size      : 24,
            hints     : [gettext('Less Important'), gettext('Important'), gettext('Very Important')],
            starOff   : 'star-off.png',
            starOn    : 'star-on.png',
            number    : 3,
            path      : $.chasebot.STATIC_URL + 'raty/lib/img'
        });
    });
}

// This binds the single rating class within the add or edit form
function bind_rating_form() {
    "use strict";
    var i;
    $('#star').raty({
        cancel    : true,
        cancelOff : 'cancel-off-big.png',
        cancelOn  : 'cancel-on-big.png',
        cancelHint: gettext('Cancel this rating'),
        half      : false,
        size      : 24,
        hints     : [gettext('Less Important'), gettext('Important'), gettext('Very Important')],
        starOff   : 'star-off-big.png',
        starOn    : 'star-on-big.png',
        number    : 3,
        path      : $.chasebot.STATIC_URL + 'raty/lib/img',
        click     : function (score, evt) {
            if (score) {
                $('#id_important_client_' + score).attr('checked', true);
            } else {
                $('#id_important_client_0').attr('checked', true);
            }
        }
    });

    for (i = 1; i <= 3; i++) {
        if ($('#id_important_client_' + i).is(':checked')) {
            $('#star').raty('score', i);
        }
    }
}

function clear_filter(event) {
    "use strict";
    event.preventDefault();
    var ths = event.currentTarget;
    $(ths).siblings('input').val('');
    $(ths).closest('form').submit();
}

function rebind_filters(source, rebind_func) {
    "use strict";
    $(source).find(".form-filter-ajax").off('submit').on('submit', {rebind_func: rebind_func}, filter_rows);
    $(source).find(".filter-close").off('click').on('click', clear_filter);
}

function new_conversation(event) {
    "use strict";
    event.preventDefault();
    var contact_id, url, row;
    if ($(event.currentTarget).hasClass('active')) {
        $('#new_conversation_id').remove();
        return;
    }

    contact_id = $('#contact_id').text();
    url = '/contact/' + contact_id + '/call/add/';
    row = $('<tr/>', {id: 'new_conversation_id'});
    row.load(url, function (result) {
        $('#search_result').prepend(row);
        reload_edit_save_cancel_buttons($(row), url, true);
        bind_attach_deal(row);
    });
}

function chosenify_field(field_id, source) {
    "use strict";
    $(field_id, source).chosen({no_results_text: gettext('No results match')});
}

function edit_new_event(event) {
    "use strict";
    event.preventDefault();
    var url;
    url = $(event.currentTarget).attr("href");
    $('#event_modal').empty();
    $('#event_modal').load(url, function (result) {
        $("#event_form").get(0).setAttribute("action", url);
        show_modal($(this), '30em');
        rebind_events('#events_pane');
    });
}

function add_more_tag_to_all_notefields(source) {
    "use strict";
    var showChars, ellipsesText, moreText, lessText, bag, countChars, openTags;
    showChars = 135;
    ellipsesText = "...";
    moreText = gettext("more");
    lessText = gettext("less");

    $('.cb_notes:not(:has(*))', source).each(function () {
        var $this, content, c, inTag, i, tagName, j, html, tmp;
        $this = $(this);
        content = $this.html();
        if (content.length > showChars) {
            c = content.substr(0, showChars);
            if (c.indexOf('<') >= 0) { // If there's HTML don't want to cut it            
                inTag = false; // I'm in a tag?
                bag = ''; // Put the characters to be shown here
                countChars = 0; // Current bag size
                openTags = []; // Stack for opened tags, so I can close them later

                for (i = 0; i < content.length; i++) {
                    if (content[i] === '<' && !inTag) {
                        inTag = true;

                        // This could be "tag" or "/tag"
                        tagName = content.substring(i + 1, content.indexOf('>', i));

                        // If its a closing tag
                        if (tagName[0] === '/') {
                            if (tagName !== '/' + openTags[0]) {
                                tmp = 1 + 1; //dummy to pass lint
                            } else {
                                openTags.shift(); // Pops the last tag from the open tag stack (the tag is closed in the retult HTML!)
                            }
                        } else {
                            // There are some nasty tags that don't have a close tag like <br/>
                            if (tagName.toLowerCase() !== 'br') {
                                openTags.unshift(tagName);
                            }
                        }
                    }
                    if (inTag && content[i] === '>') {
                        inTag = false;
                    }

                    if (inTag) {
                        bag += content[i]; // Add tag name chars to the result
                    } else {
                        if (countChars < showChars) {
                            bag += content[i];
                            countChars++;
                        } else {
                            if (openTags.length > 0) {
                                for (j = 0; j < openTags.length; j++) {
                                    bag += '</' + openTags[j] + '>';
                                    // You could shift the tag from the stack to check if you end with an empty stack, that means you have closed all open tags
                                }
                                break;
                            }
                        }
                    }
                }
                c = bag;
            }

            html = '<span class="shortcontent">' + c + '&nbsp;' + ellipsesText +
                   '</span><span class="allcontent">' + content +
                   '</span>&nbsp;&nbsp;<span><a href="javascript:void(0)" class="morelink badge">' + moreText + '</a></span>';

            $this.html(html);
            $(".allcontent").hide();
        }
    });

    $(".morelink").off('click').on('click', function () {
        var $this = $(this);

        if ($this.hasClass('less')) {
            $this.removeClass('less');
            $this.html(moreText);

            $this.parent().prev().prev().show(); // shortcontent
            $this.parent().prev().hide(); // allcontent       
        } else {
            $this.addClass('less');
            $this.html(lessText);

            $this.parent().prev().prev().hide(); // shortcontent
            $this.parent().prev().show(); // allcontent
        }
        return false;
    });
}

function event_modal_add_save(event) {
    "use strict";
    event.preventDefault();
    var modal, events_pane, form, url, data;
    modal = $(event.data.modal);
    events_pane = $(event.data.events_pane);
    form = $(event.data.form);
    url = $(form).attr('action');
    data = $(form).serialize();

    $.post(url, data, function (result) {
        //If there are validation errors upon adding the field
        if ($('#validation_error_ajax', result).text() === 'True') {
            modal.empty();
            modal.append(result);
            $("#event_form").get(0).setAttribute("action", url);
            rebind_events('#events_pane');
        } else {
            //if there is no error then insert the added row before the current add-button row. (last row)
            $(modal).modal('hide');
            $(modal).empty();
            $(events_pane).empty();
            $(events_pane).append(result);
            rebind_events('#events_pane');
        }
    });
}

function rebind_events(source) {
    "use strict";
    var src = '#tab_open_deals';
    if (source) {
        src = source;
    }
    rebind_delete_paginator(src, '#events_pane', rebind_events);
    $(src).find(".row_edit_event").click(edit_new_event);
    add_more_tag_to_all_notefields(src);

    $('#event_form').submit({modal: '#event_modal', events_pane: '#events_pane', form: '#event_form'}, event_modal_add_save);
    datepicker_reload('#event_modal', false);
    $('#event_modal_save_btn').off('click').on('click', function (event) {
        event.preventDefault();
        $('#event_form').submit();
    });
}

function deal_submit(url, form, modal) {
    "use strict";
    var data;
    data = $(form).serialize();
    $.post(url, data, function (result) {
        //If there are validation errors upon adding the field
        if ($('#validation_error_ajax', result).text() === 'True') {
            form.empty();
            form.append(result);
            chosenify_field('#id_sales_item', '#deal_modal_body');
            datepicker_reload('#deal_modal_body', false);
            calc_total_value();
        } else {
            //if there is no error then insert the added row before the current add-button row. (last row)
            $(modal).modal('hide');
            $('#tab_open_deals').empty();
            $('#tab_open_deals').append(result);
            rebind_open_deals(true);
        }
    });
}

function negotiate_deal(event) {
    "use strict";
    event.preventDefault();
    event.stopPropagation();
    var url, form;
    url = $(event.currentTarget).attr("href");
    $('#deal_modal_body').empty();
    form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'post'});
    $('#deal_modal_body').append(form);
    form.load(url, function (result) {
        show_modal('#deal_modal');
        $(this).get(0).setAttribute("action", url);
        datepicker_reload('#deal_modal_body', false);
        chosenify_field('#id_sales_item', '#deal_modal_body');
        calc_total_value();
        $('#deal_modal').find('#modal_h3').text(gettext('Negotiate Deal'));
        $('#modal_icon').html('<i class="icon-pencil icon-large"></i>');
        $(this).submit({modal: '#deal_modal', form: $(this), url: url}, function (event) {
            event.preventDefault();
            deal_submit(event.data.url, event.data.form, event.data.modal);
        });
        var validator = validation_rules('#deal_modal_form');
        $('#deal_modal').find('#deal_modal_confirm_btn').off('click').on('click', {validator: validator}, function () {
            validator.form();
            if (validator.numberOfInvalids() === 0) {
                $('#deal_modal').modal('hide');
                $.post(url, form.serialize(), function (result) {
                    $('#tab_open_deals').empty();
                    $('#tab_open_deals').append(result);
                    rebind_open_deals(true);
                });
                //form.submit();
            }
        });
        draggable_modal('#deal_modal');
    });
}

function load_business_card(event) {
    "use strict";
    event.preventDefault();
    event.stopPropagation();
    var url = $(event.currentTarget).attr("href");
    $('#business_card_modal').load(url, function (result) {
        rebind_ratings($('#business_card_modal'));
        $(this).modal('show');
    });
    draggable_modal('#business_card_modal');
}

function fill_new_deal_from_template_data(selected_id) {
    "use strict";
    var url, source;
    source = $('#deal_modal_body');
    url = 'deal_template/' + selected_id + '/';
    //Here we make an ajax call to the server to get the data from the selected deal Template or get the data from the last open deal instance,
    //In either case the user can then override these values  
    $.ajax({
        type: 'GET',
        url: url,
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (data) {
            var template_name, deal_instance_name, vals, i, validator;
            template_name = data[0].fields.deal_name;

            // Set all the values from json into the cloned fields accordingly
            //Attention, when setting ANY field to the value from json follow these rules: 
            // Set the value for all inputs with .attr('value', foo)
            // Set the value for all dropdowns with val() so that the primary key is used.
            // for m2m you need to use val() on an array (see below)

            source.find('#id_deal_instance_name').attr('value', '');
            source.find('#id_deal_template_name').attr('value', template_name);
            source.find('#id_deal_description').text(data[0].fields.deal_description);
            source.find('#id_sales_term').val(data[0].fields.sales_term);
            source.find('#id_price').attr('value', data[0].fields.price);
            source.find('#id_currency').val(data[0].fields.currency);
            source.find('#id_quantity').attr('value', data[0].fields.quantity);

            if (data[0].fields.hasOwnProperty('status')) {
                source.find('#id_status').val(data[0].fields.status);
            } else {
                source.find('#id_status>option:eq(1)').prop('selected', true);
            }

            if (data[0].fields.hasOwnProperty('deal_template')) {
                source.find('#id_deal_template').val(data[0].fields.deal_template);
            } else {
                source.find('#id_deal_template').val(data[0].pk);
            }

            //m2m needs special treatment with arrays
            source.find('#id_sales_item').val('');
            vals = [];
            for (i = 0; i <= data[0].fields.sales_item.length; i++) {
                vals.push(data[0].fields.sales_item[i]);
            }
            source.find('#id_sales_item').val(vals);
            source.find('#id_sales_item').chosen({no_results_text: gettext('No results match')});
            calc_total_value();
            calc_totals();
            validator = validation_rules('#deal_from_template_form');
            $('#deal_modal').find('#deal_modal_confirm_btn').off('click').on('click', {validator: validator}, function (event) {
                validator = event.data.validator;
                validator.form();
                if (validator.invalidElements().length > 0) {
                    return;
                }
                deal_submit('open_deals/add_new_from_template/', $('#deal_from_template_form'), '#deal_modal');
            });
            $('#deal_modal').find('#deal_modal_confirm_btn').show();
        }
    });
}



function new_deal_from_template(event) {
    "use strict";
    event.preventDefault();
    var url = 'open_deals/add_new_from_template/';
    $('#deal_modal_body').empty();
    $.get(url, function (result) {
        $('#deal_modal_body').append(result);
        $('#deal_modal_body').find('#add_deals_button').off('click').on('click', function (event) {
            event.preventDefault();
            var selected_id;
            selected_id = $('#deal_modal_body').find('.pre_defined_deal_dropdown option:selected').val();
            $('#add_deals_dropdown').remove();
            $('#deal_from_template_div').show();
            fill_new_deal_from_template_data(selected_id, $('#deal_modal_body'));
            $('#deal_modal').find('#deal_modal_confirm_btn').show();
        });
        $('#deal_modal').find('#deal_modal_confirm_btn').hide();
        $('#deal_modal').find('#modal_h3').text(gettext('Add New Deal From Template'));
        show_modal('#deal_modal');
        draggable_modal('#deal_modal');
    });
}


function new_deal(event) {
    "use strict";
    event.preventDefault();
    var url;
    url = 'open_deals/add_new/';
    $('#deal_modal_body').empty();
    $.get(url, function (result) {
        var form, validator;
        //Form is only required for validation, but it doesn't submit
        form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'}).append(result);
        $('#deal_modal_body').append(form);
        calc_total_value();
        $('#deal_modal_body').find('.deal_status').val(1);
        validator = validation_rules('#deal_modal_form');
        $('#deal_modal').find('#deal_modal_confirm_btn').off('click').on('click', {validator: validator}, function (event) {
            validator = event.data.validator;
            validator.form();
            if (validator.invalidElements().length > 0) {
                return;
            }
            deal_submit(url, form, '#deal_modal');
        });
        $('#deal_modal').find('#deal_modal_confirm_btn').show();
        $('#deal_modal').find('#modal_h3').text(gettext('Create Your Own Deal'));
        show_modal('#deal_modal');
        draggable_modal('#deal_modal');
    });
}

function rebind_open_deals(load_sorttable) {
    "use strict";
    if (load_sorttable) {
        sort_table('#open_deal_table', '#open_deal_tabs');
    } else {
        // let the plugin know that we made a update
        // the resort flag set to anything BUT false (no quotes) will trigger an automatic
        // table resort using the current sort
        var resort = true;
        $("#open_deal_table").trigger("update", [resort]);
    }
    $('.business_card_modal_link').off('click').on('click', load_business_card);
    $(".negotiate_deal_btn").off('click').on('click', negotiate_deal);
    $("#new_deal").off('click').on('click', new_deal);
    $("#add_deal_template").off('click').on('click', new_deal_from_template);
    rebind_paginator('#open_deal_table', '#search_result', rebind_open_deals);
    $('.event_calls_btn').off('click').on('click', function (event) {
        event.preventDefault();
        var clicked_on_same_row, deal_row, tr, url, row, more_btn;
        clicked_on_same_row = false;
        deal_row = $(this).closest('tr');
        if (deal_row.next('#details').length === 1) {
            clicked_on_same_row = true;
        }
        $(".collapse").collapse('toggle');
        $('.collapse').on('hidden', {deal_row: deal_row}, function () {
            deal_row.siblings('#details').remove();
        });

        if (clicked_on_same_row) {
            $(this).children('.icon-double-angle-up').addClass('icon-double-angle-down').removeClass('icon-double-angle-up');
            $(this).children('.more_text').text(gettext('More'));
            rebind_paginator('#open_deal_table', '#search_result', rebind_open_deals);
            return;
        }
        more_btn = $(this);
        url = deal_row.find('#open_deal_url').text();
        row = $('<tr/>', {id: 'details'});

        row.load(url, function (result) {
            row.insertAfter(deal_row);
            row.find('#new_event_button').off('click').on('click', edit_new_event);
            rebind_events();
            $(".collapse").collapse('toggle');
            more_btn.children('.icon-double-angle-down').addClass('icon-double-angle-up').removeClass('icon-double-angle-down');
            more_btn.children('.more_text').text(gettext('Less'));
        });
    });
}

function reword_collapseable(parent) {
    "use strict";
    $(parent).on('shown', function () {
        $('#collapse_event_head').text(gettext("Less Details"));
    });
    $(parent).on('hidden', function () {
        $('#collapse_event_head').text(gettext("More Details"));
    });
}

function rebind_business_card_modal_link() {
    "use strict";
    $('.business_card_modal_link').off('click').on('click', load_business_card);
}

function tab_deal_templates_clicked() {
    "use strict";
    $('#tab_sales_items').empty();
    $('#tab_contacts').empty();
    $('#tab_open_deals').empty();
    $('#deal_modal_body').empty();
    $('#tab_todo').empty();
    $('#tab_deal_templates').load('deal_templates/', function (result) {
        rebind_deal_templates();
    });
    $('#main_tabs a[href="#tab_deal_templates"]').off('click');
    bind_main_tabs('tab_deal_templates');
    $('#sidebar').load('sidebar/deal_templates/', function (result) {
        $('#sidebar').find(".typeahead_deals_deal_name").typeahead({ source: typeahead_deals_deal_name });
        $('#sidebar').find(".typeahead_deals_sales_item").typeahead({ source: typeahead_deals_sales_item });
        $('#sidebar').find(".typeahead_deals_price").typeahead({ source: typeahead_deals_price });
        $('#sidebar').find(".typeahead_deals_sales_term").typeahead({ source: typeahead_deals_sales_term });
        $('#sidebar').find(".typeahead_deals_quantity").typeahead({ source: typeahead_deals_quantity });
        rebind_filters('#sidebar', rebind_deal_templates);
    });
}

function bind_sales_item_btn() {
    "use strict";
    $("#modal_sales_items_btn").off('click').on('click', function (event) {
        event.preventDefault();
        var url = $(this).attr("href") + "/";
        $("#sales_items_modal_body").load(url, function (result) {
            $('#salesitems_modal').on('hide', function () {
                $('#deal_template_sales_item').load('sales_items/deal_template/', function (result) {
                    chosenify_field('#id_sales_item', '#deal_template_sales_item');
                    bind_sales_item_btn();
                });
            });
            $('#salesitems_modal').modal('show'); // display the modal on url load            
            rebind_sales_item('#tab_deal_templates');
        });
    });
}

function deal_template_add_edit(event) {
    "use strict";
    event.preventDefault();
    var url, validator;
    url = $(event.currentTarget).attr('href');
    $('#tab_deal_templates').load(url, function (result) {
        validator = validation_rules('#deal_template_form_id');
        chosenify_field('#id_sales_item', $(this));

        $(this).find('#back2deal_templates').off('click').on('click', function (event) {
            event.preventDefault();
            tab_deal_templates_clicked();
        });

        $('#deal_template_form_id').submit({url: url}, function (event) {
            event.preventDefault();
            var url, data;
            url = event.data.url;
            data = $(this).serialize();
            $.post(url, data, function (result) {
                $('#tab_deal_templates').empty();
                $('#tab_deal_templates').append(result);
                rebind_deal_templates();
            });
        });

        $('#deal_template_save_btn').off('click').on('click', {validator: validator}, function (event) {
            event.preventDefault();
            validator.form();
            if (validator.numberOfInvalids() === 0) {
                $('#deal_template_form_id').submit();
            }
        });

        $('#deal_template_cancel_btn').off('click').on('click', function (event) {
            event.preventDefault();
            tab_deal_templates_clicked();
        });

        bind_sales_item_btn();
    });
}

function tab_contacts_clicked() {
    "use strict";
    $('#tab_sales_items').empty();
    $('#tab_open_deals').empty();
    $('#tab_deal_templates').empty();
    $('#deal_modal_body').empty();
    $('#tab_todo').empty();
    $('#tab_contacts').load('contacts/', function (result) {
        rebind_contacts();
    });
    $('#main_tabs a[href="#tab_contacts"]').off('click');
    bind_main_tabs('tab_contacts');
    $('#sidebar').load('sidebar/contacts/', function (result) {
        $('#sidebar').find(".typeahead_contacts_last_name").typeahead({ source: typeahead_contacts_last_name });
        $('#sidebar').find(".typeahead_contacts_first_name").typeahead({ source: typeahead_contacts_first_name });
        $('#sidebar').find(".typeahead_contacts_company").typeahead({ source: typeahead_contacts_company });
        $('#sidebar').find(".typeahead_contacts_email").typeahead({ source: typeahead_contacts_email });
        rebind_filters('#sidebar', rebind_contacts);
    });
}

function rebind_conversations(source) {
    "use strict";
    var target, src;
    target = '#search_result';
    if (source) {
        src = source;
    } else {
        src = '#tab_contacts';
    }
    rebind_ratings($('#business_card_modal'));
    rebind_delete_paginator(src, target, rebind_conversations);
    $(src).find(".row_edit_ajax").off('click').on('click', {source: src}, row_edit_ajax);
    $('.back2contacts').off('click').on('click', function (event) {
        event.preventDefault();
        tab_contacts_clicked();
    });
    $('#new_conversation_button').off('click').on('click', new_conversation);
    rebind_filters($('#sidebar'), rebind_conversations);
    add_more_tag_to_all_notefields(src);
    draggable_modal('#business_card_modal');
}

function rebind_sales_item(source) {
    "use strict";
    var target = '#search_result';
    rebind_delete_paginator(source, target, partial(rebind_sales_item, source));
    $(source).find(".row_edit_ajax").off('click').on('click', {source: source}, row_edit_ajax);
    //save_add_form currently only used for sales item
    $('#save_add_form').off('submit').on('submit', {source: source}, row_add_save_sales_item);
    $('#sales_item_filter').find(".form-filter-ajax").off('submit').on('submit', {rebind_func: partial(rebind_sales_item, source)}, filter_rows);
    $('#sales_item_filter').find(".typeahead_sales_items").typeahead({ source: typeahead_sales_items });
    $('#sales_item_filter').find(".filter-close").off('click').on('click', clear_filter);
    $('#sidebar').find(".typeahead_sales_items").typeahead({ source: typeahead_sales_items });
}

function conversation_clicked(event) {
    "use strict";
    event.preventDefault();
    var url = $(event.currentTarget).attr('href');
    $('#tab_contacts').load(url, function (result) {
        $('#sidebar').load('sidebar/contact/' + $('#contact_id').text() + '/conversations/', function (result) {
            $('#sidebar').find(".typeahead_calls_from_date").typeahead({ source: typeahead_opendeal_deal_name });
            $('#sidebar').find(".typeahead_calls_to_date").typeahead({ source: typeahead_opendeal_status });
            rebind_filters('#sidebar', rebind_conversations);
            datepicker_reload('#sidebar', true);
        });
        rebind_conversations('#tab_contacts');
    });
}

function add_edit_new_contact(event) {
    "use strict";
    event.preventDefault();
    var url = $(event.currentTarget).attr('href');

    $('#tab_contacts').load(url, function (result) {
        $('#back2contacts').off('click').on('click', function (event) {
            event.preventDefault();
            tab_contacts_clicked();
        });

        $('#contact_cancel_btn').off('click').on('click', function (event) {
            event.preventDefault();
            tab_contacts_clicked();
        });

        datepicker_reload('#tab_contacts', true);
        bind_rating_form();

        $('#contact_form_id').submit({url: url}, function (event) {
            event.preventDefault();
            var url, data;
            url = event.data.url;
            data = $(this).serialize();
            $.post(url, data, function (result) {
                $('#tab_contacts').empty();
                $('#tab_contacts').append(result);
                rebind_contacts();
            });
        });

        var validator = validation_rules('#contact_form_id');
        $('#tab_contacts').find('#contact_save_btn').off('click').on('click', {validator: validator}, function () {
            validator.form();
            if (validator.numberOfInvalids() === 0) {
                $('#contact_form_id').submit();
            }
        });
    });
}

function rebind_contacts() {
    "use strict";
    var source, target;
    source = '#tab_contacts';
    target = '#search_result';
    rebind_ratings($('#search_result'));
    rebind_delete_paginator(source, target, rebind_contacts);
    $(source).find(".row_edit_ajax").off('click').on('click', {source: source}, row_edit_ajax);
    rebind_business_card_modal_link();
    $('.conversation_btn').off('click').on('click', conversation_clicked);
    $('#add_new_contact_btn').off('click').on('click', add_edit_new_contact);
    $('.row_edit_contact_btn').off('click').on('click', add_edit_new_contact);
}

function rebind_deal_templates() {
    "use strict";
    var source, target;
    source = '#tab_deal_templates';
    target = '#search_result';
    $(source).find('.deal_template_edit_btn').off('click').on('click', deal_template_add_edit);
    $('#new_deal_template_btn').off('click').on('click', deal_template_add_edit);
    rebind_delete_paginator(source, target, rebind_deal_templates);
    add_more_tag_to_all_notefields(source);
}

function tab_open_deals_clicked(deal_id) {
    "use strict";
    $('#tab_sales_items').empty();
    $('#tab_contacts').empty();
    $('#tab_deal_templates').empty();
    $('#deal_modal_body').empty();
    $('#tab_todo').empty();
    $('#tab_open_deals').load('open_deals/', function (result) {
        rebind_open_deals(true);
        if (deal_id) {
            $('#tab_open_deals tbody tr').each(function (index, value) {
                if ($(this).find('#open_deal_uuid').text() === deal_id) {
                    $(this).find('.event_calls_btn').click();
                }
                //Todo: Else go to server and see in which page it is
            });
        }
    });
    $('#main_tabs a[href="#tab_open_deals"]').off('click');
    bind_main_tabs('tab_open_deals');
    $('#sidebar').load('sidebar/open_deals/', function (result) {
        $('#sidebar').find(".typeahead_opendeal_deal_name").typeahead({ source: typeahead_opendeal_deal_name });
        $('#sidebar').find(".typeahead_opendeal_status").typeahead({ source: typeahead_opendeal_status });
        $('#sidebar').find(".typeahead_opendeal_total_value").typeahead({ source: typeahead_opendeal_total_value });
        datepicker_reload('#sidebar', true);
        rebind_filters('#sidebar', rebind_open_deals);
        $("<img />", {'class': 'funnel', src: $.chasebot.STATIC_URL + 'img/funnel.png'}).load(function () {
            var h4 = $('<h4 />', {'class': 'funnel'}).append(gettext('Sales Funnel'));
            $('#sidebar').append(h4);
            $(this).appendTo($('#sidebar'));
        });
    });
}

function rebind_event_tick() {
    "use strict";
    var source = '#tab_todo';
    $('.row_event_tick_btn').off('click').on('click', function (event) {
        event.preventDefault();
        if (confirm(gettext('Are you sure you want to tick off this event and remove it?'))) {
            var url = $(this).attr("href");
            $.post(url, function (result) {
                $('#tab_todo').empty();
                $('#tab_todo').append(result);
                rebind_event_tick();
            });
        }
    });

    $('.todo_event_tr').off('click').on('click', function (event) {
        event.preventDefault();
        $('#main_tabs a[href="#tab_open_deals"]').tab('show');
        tab_open_deals_clicked($(this).attr('id'));
    });
    add_more_tag_to_all_notefields(source);
}

function tab_todo_clicked() {
    "use strict";
    $('#tab_sales_items').empty();
    $('#tab_contacts').empty();
    $('#tab_open_deals').empty();
    $('#tab_deal_templates').empty();
    $('#deal_modal_body').empty();
    $('#tab_todo').load('events/', function (result) {
        rebind_event_tick();
    });
    $('#main_tabs a[href="#tab_todo"]').off('click');
    bind_main_tabs('tab_todo');
    $('#sidebar').load('sidebar/todo/', function (result) {
        $('#feedback_btn').removeClass('hidden');
    });
}

function tab_contacts_clicked() {
    "use strict";
    $('#tab_sales_items').empty();
    $('#tab_open_deals').empty();
    $('#tab_deal_templates').empty();
    $('#deal_modal_body').empty();
    $('#tab_todo').empty();
    $('#tab_contacts').load('contacts/', function (result) {
        rebind_contacts();
    });
    $('#main_tabs a[href="#tab_contacts"]').off('click');
    bind_main_tabs('tab_contacts');
    $('#sidebar').load('sidebar/contacts/', function (result) {
        $('#sidebar').find(".typeahead_contacts_last_name").typeahead({ source: typeahead_contacts_last_name });
        $('#sidebar').find(".typeahead_contacts_first_name").typeahead({ source: typeahead_contacts_first_name });
        $('#sidebar').find(".typeahead_contacts_company").typeahead({ source: typeahead_contacts_company });
        $('#sidebar').find(".typeahead_contacts_email").typeahead({ source: typeahead_contacts_email });
        rebind_filters('#sidebar', rebind_contacts);
    });
}

function tab_sales_items_clicked() {
    "use strict";
    $('#sidebar').empty();
    $('#tab_contacts').empty();
    $('#tab_open_deals').empty();
    $('#tab_deal_templates').empty();
    $('#deal_modal_body').empty();
    $('#tab_todo').empty();
    $('#tab_sales_items').load('sales_items/', function (result) {
        rebind_sales_item('#tab_sales_items');
    });
    $('#main_tabs a[href="#tab_sales_items"]').off('click');
    bind_main_tabs('tab_sales_items');
}

function bind_main_tabs(optionalArg) {
    "use strict";
    //Exclude the passed in tab name from being subscribed to the click event. (So that repetetive clicking on active tab
    // is ignored. However the other tabs get subscribed at the same time.
    optionalArg = (optionalArg === "undefined") ? null : optionalArg;
    if (optionalArg !== 'tab_contacts') {
        $('#main_tabs a[href="#tab_contacts"]').off('click').on('click', tab_contacts_clicked);
    }
    if (optionalArg !== 'tab_open_deals') {
        $('#main_tabs a[href="#tab_open_deals"]').off('click').on('click', tab_open_deals_clicked);
    }
    if (optionalArg !== 'tab_deal_templates') {
        $('#main_tabs a[href="#tab_deal_templates"]').off('click').on('click', tab_deal_templates_clicked);
    }
    if (optionalArg !== 'tab_todo') {
        $('#main_tabs a[href="#tab_todo"]').off('click').on('click', tab_todo_clicked);
    }
    if (optionalArg !== 'tab_sales_items') {
        $('#main_tabs a[href="#tab_sales_items"]').off('click').on('click', tab_sales_items_clicked);
    }
}

function initialize_validator() {
    "use strict";
    // add the rule here
    $.validator.addMethod("valueNotEquals", function (value, element, arg) {
        return arg !== value;
    }, gettext('Please select an item!'));

    $.validator.addMethod("xrequire_from_group", $.validator.methods.require_from_group, gettext('Either the last name OR the company name are required.'));

    $.validator.addClassRules("fillone", {
        xrequire_from_group: [1, ".fillone"]
    });

    $.validator.addClassRules("email", {
        email: true
    });

    $.validator.addClassRules("quantity", {
        required: true,
        digits: true
    });

    $.validator.addClassRules("price", {
        required: true,
        number: true
    });

    $.validator.addClassRules("input_mandatory", {
        required: true
    });

    $.validator.addClassRules("textarea_mandatory", {
        required: true
    });

    $.validator.addClassRules("date_picker", {
        date: true
    });
}

function spinning_btn(btn_id, form_id) {
    "use strict";
    $(btn_id).click(function (event) {
        event.preventDefault();
        $(this).off('click');
        $(this).addClass('disabled');
        $(this).html('<i class="icon-spinner icon-spin"></i> Please wait...');
        $(form_id).submit();
    });
}

function activate_menu(event) {
    "use strict";
    event.preventDefault();
    var i, menu_id;
    menu_id = event.data.menu_id;
    for (i = 0; i < $(menu_id).parent().children().length; i++) {
        $(menu_id).parent().children()[i].removeClass('active');
    }
    $(menu_id).addClass('active');
}

$(document).ready(function () {
    "use strict";
    initialize_validator();
    bind_main_tabs();

    $('#timezone_dropdown').change(function (event) {
        event.preventDefault();
        $('#timezone_form').submit();
    });

    $('.timezone_help').click(function (event) {
        event.preventDefault();
        $('#timezone_dropdown').popover('toggle');
        isVisible = true;
    });

    spinning_btn('#demo-button', '#form_demo');
    spinning_btn('#invite-button', '#form_invite');
    spinning_btn('#registration-button', '#form_registration');
    spinning_btn('#login-button', '#form_login');
    spinning_btn('#reset-button', '#form_reset');

    $('#invite_menu').on('click').off('click', {menu_id: '#invite_menu'}, activate_menu);
    $('#home_menu').on('click').off('click', {menu_id: '#home_menu'}, activate_menu);

	$('#feedback_btn').off('click').on('click', function (event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $('#feedback_modal_body').load(url, function (result) {
            var validator = validation_rules('#feedback_form');
            $('#feedback_send_btn').off('click').on('click', {validator: validator}, function (event) {
                var data, validator;
                validator = event.data.validator;
                validator.form();
                if (validator.numberOfInvalids() === 0) {
                    data = $('#feedback_form').serialize();
                    $.post(url, data, function (result) {
                        //Don't wait for feedback to be sent.
                        $('#messages_id').empty();
                        $('#messages_id').append(result);
                    });
                    $('#feedback_modal').modal('hide');
                }
            });
            show_modal('#feedback_modal');
        });
	});

    tab_todo_clicked();
});