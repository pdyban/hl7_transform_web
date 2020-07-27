var supported_rules = {
  'add_values': create_rule_add_values,
  'concatenate_values': create_rule_concatenate_values,
  'copy_value': create_rule_copy_value,
  'generate_alphanumeric_id': create_rule_generate_alphanumeric_id,
  'generate_current_datetime': create_rule_generate_current_datetime,
  'generate_numeric_id': create_rule_generate_numeric_id,
  'set_end_time': create_rule_set_end_time,
  'set_value': create_rule_set_value,
}

$(function() {
  for (const [name, factory] of Object.entries(supported_rules)) {
    var el = document.createElement('a');
    el.className = 'dropdown-item';
    el.href = '#';
    el.innerHTML = name;
    $(el).on('click', function(e){
        addEmptyRule(name);
    });
    $('.dropdown-menu').append(el);
  };
  var div = document.createElement('div')
  div.className = 'dropdown-divider'
  $('.dropdown-menu').append(div)
  var el = document.createElement('a');
  el.className = 'dropdown-item';
  el.href = 'https://hl7-transform.readthedocs.io/en/latest/mapping.html#list-of-supported-operations';
  el.setAttribute('target', 'help');
  el.innerHTML = 'Full list of mapping rules';
  $('.dropdown-menu').append(el);
  if($("#mapping_scheme").length) {
    updateQuickView();
  }
});

$("#advanced-tab").on('click', function(e) {
  updateAdvancedView();
});

$("#quick-tab").on('click', function(e) {
  updateQuickView();
});

$(document).on('click', '.icon-delete', function () {
   $(this).closest('li').remove();
});

$("#transform-btn").on('click', function(e) {
  updateAdvancedView();
});

function updateAdvancedView() {
  console.log('updateAdvancedView');
  var l = [];

  function convertToDict(item) {
    var operation_dict = {}
    var rule_name = $(item).children('div[name="rule-name"]');
    if (rule_name.length) {
      operation_dict['operation'] = rule_name.html();
    }

    var target_field = $(item).find('div').children('input[name="rule-target-field"]');
    if (target_field.length) {
      operation_dict['target_field'] = target_field.val();
    }

    var source_field = $(item).find('div').children('input[name="rule-source-field"]');
    if (source_field.length) {
      operation_dict['source_field'] = source_field.val();
    }

    var start_time = $(item).find('div').children('input[name="rule-start-time-field"]');
    var duration = $(item).find('div').children('input[name="rule-duration-field"]');
    if (start_time.length && duration.length) {
      operation_dict['source_fields'] = [start_time.val(), duration.val()];
    }

    if (!(operation_dict.hasOwnProperty('args'))) {
      operation_dict['args'] = {}
    }

    var operands = $(item).find('div').children('input[name="rule-operand-field"]');
    var valuetype = $(item).find('div').children('select[name="rule-value-type-field"]');
    if (operands.length > 1 && valuetype.length) {
      ops = []
      $.each(operands, function(index, item){ops.push($(item).val())});
      operation_dict['source_fields'] = ops;
      operation_dict['args']['type'] = valuetype.val();
    }

    var value = $(item).find('div').children('input[name="rule-value"]');
    if (value.length) {
      operation_dict['args']['value'] = value.val();
    }

    var separator = $(item).find('div').children('input[name="rule-separator"]');
    if (separator.length) {
      operation_dict['args']['separator'] = separator.val();
    }
    if (Object.keys(operation_dict['args']).length == 0) {
      delete operation_dict['args'];
    }
    return operation_dict;
  };
  // for rule in rule-list: convert to dict
  $.each($('ul#rule-list li'), function(index, item) { dict = convertToDict(item); l.push(dict)});
  // prettify and write dict as JSON to textarea
  $('#mapping_scheme').val(JSON.stringify(l, null, 2));
};

function updateQuickView() {
  // clear all existing rules
  $('#rule-list').empty();
  try {
    // read textarea text as list of dicts
    var json_string = $('#mapping_scheme').val();
    if(json_string.length > 0) {
      rules = JSON.parse(json_string);
      // for item in list: create a rule
      rules.forEach(rule => addRule(rule));
    }
  }
  catch(err) {
    alert('Mapping scheme could not be parsed as JSON.');
    console.log(err);
  }
};

function addRule(dict) {
  var li = addEmptyRule(dict['operation']);
  if (li == null) {
    alert('Could not create rule ' + dict['operation']);
  }
  var target_field = $(li).find('div').children('input[name="rule-target-field"]');
  if (dict.hasOwnProperty('target_field') && target_field != null) {
    target_field.val(dict['target_field']);
  }

  var source_field = $(li).find('div').children('input[name="rule-source-field"]');
  if (dict.hasOwnProperty('source_field') && source_field != null) {
    source_field.val(dict['source_field']);
  }

  var value = $(li).find('div').children('input[name="rule-value"]');
  if (dict.hasOwnProperty('args') && dict['args'].hasOwnProperty('value') && value != null) {
    value.val(dict['args']['value']);
  }

  var start_time = $(li).find('div').children('input[name="rule-start-time-field"]');
  if (dict.hasOwnProperty('source_fields') && dict['source_fields'].length > 1 && start_time != null) {
    start_time.val(dict['source_fields'][0]);
  }

  var duration = $(li).find('div').children('input[name="rule-duration-field"]');
  if (dict.hasOwnProperty('source_fields') && dict['source_fields'].length > 1 && duration != null) {
    duration.val(dict['source_fields'][1]);
  }

  var operands = $(li).find('div').children('input[name="rule-operand-field"]');
  if (dict.hasOwnProperty('source_fields') && dict['source_fields'].length == 2 && operands != null) {
    $(operands[0]).val(dict['source_fields'][0]);
    $(operands[1]).val(dict['source_fields'][1]);
  }

  var valuetype = $(li).find('div').children('select[name="rule-value-type-field"]');
  if(valuetype != null && dict.hasOwnProperty('args') && dict['args'].hasOwnProperty('type')) {
    valuetype.val(dict['args']['type']);
  }

  var separator = $(li).find('div').children('input[name="rule-separator"]');
  if (dict.hasOwnProperty('args') && dict['args'].hasOwnProperty('separator') && separator != null) {
    separator.val(dict['args']['separator']);
  }
}

function createLi() {
  var li = document.createElement('li');
  li.className = 'list-group-item d-flex flex-row';
  return li
}

function create_rule_set_value() {
  var li = createLi();
  li.appendChild(ruleIndexDiv($('ul#rule-list li').length+1));
  li.appendChild(ruleNameDiv('set_value'));
  li.appendChild(targetFieldDiv());
  li.appendChild(valueDiv());
  li.appendChild(helpItemDiv('https://hl7-transform.readthedocs.io/en/latest/mapping.html#hl7_transform.operations.SetValueOperation'));
  li.appendChild(deleteItemDiv());
  $('#rule-list').append(li);
  return li;
}

function create_rule_copy_value() {
  var li = document.createElement('li');
  li.className = 'list-group-item d-flex flex-row';
  li.appendChild(ruleIndexDiv($('ul#rule-list li').length+1));
  li.appendChild(ruleNameDiv('copy_value'));
  li.appendChild(targetFieldDiv());
  li.appendChild(sourceFieldDiv());
  li.appendChild(helpItemDiv('https://hl7-transform.readthedocs.io/en/latest/mapping.html#hl7_transform.operations.CopyValueOperation'));
  li.appendChild(deleteItemDiv());
  $('#rule-list').append(li);
  return li;
}

function create_rule_add_values() {
  var li = document.createElement('li');
  li.className = 'list-group-item d-flex flex-row';
  li.appendChild(ruleIndexDiv($('ul#rule-list li').length+1));
  li.appendChild(ruleNameDiv('add_values'));
  li.appendChild(targetFieldDiv());
  li.appendChild(operandDiv());
  li.appendChild(operandDiv());
  li.appendChild(valueTypeDiv());
  li.appendChild(helpItemDiv('https://hl7-transform.readthedocs.io/en/latest/mapping.html#hl7_transform.operations.AddValuesOperation'));
  li.appendChild(deleteItemDiv());
  $('#rule-list').append(li);
  return li;
}

function create_rule_generate_alphanumeric_id() {
  var li = document.createElement('li');
  li.className = 'list-group-item d-flex flex-row';
  li.appendChild(ruleIndexDiv($('ul#rule-list li').length+1));
  li.appendChild(ruleNameDiv('generate_alphanumeric_id'));
  li.appendChild(targetFieldDiv());
  li.appendChild(helpItemDiv('https://hl7-transform.readthedocs.io/en/latest/mapping.html#hl7_transform.operations.GenerateAplhanumericID'));
  li.appendChild(deleteItemDiv());
  $('#rule-list').append(li);
  return li;
}

function create_rule_generate_numeric_id() {
  var li = document.createElement('li');
  li.className = 'list-group-item d-flex flex-row';
  li.appendChild(ruleIndexDiv($('ul#rule-list li').length+1));
  li.appendChild(ruleNameDiv('generate_numeric_id'));
  li.appendChild(targetFieldDiv());
  li.appendChild(helpItemDiv('https://hl7-transform.readthedocs.io/en/latest/mapping.html#hl7_transform.operations.GenerateNumericID'));
  li.appendChild(deleteItemDiv());
  $('#rule-list').append(li);
  return li;
}

function create_rule_concatenate_values() {
  var li = document.createElement('li');
  li.className = 'list-group-item d-flex flex-row';
  li.appendChild(ruleIndexDiv($('ul#rule-list li').length+1));
  li.appendChild(ruleNameDiv('concatenate_values'));
  li.appendChild(targetFieldDiv());
  li.appendChild(operandDiv());
  li.appendChild(operandDiv());
  li.appendChild(separatorDiv());
  li.appendChild(helpItemDiv('https://hl7-transform.readthedocs.io/en/latest/mapping.html#hl7_transform.operations.ConcatenateOperation'));
  li.appendChild(deleteItemDiv());
  $('#rule-list').append(li);
  return li;
}

function create_rule_generate_current_datetime() {
  var li = document.createElement('li');
  li.className = 'list-group-item d-flex flex-row';
  li.appendChild(ruleIndexDiv($('ul#rule-list li').length+1));
  li.appendChild(ruleNameDiv('generate_current_datetime'));
  li.appendChild(targetFieldDiv());
  li.appendChild(helpItemDiv('https://hl7-transform.readthedocs.io/en/latest/mapping.html#hl7_transform.operations.GenerateCurrentDatetime'));
  li.appendChild(deleteItemDiv());
  $('#rule-list').append(li);
  return li;
}

function create_rule_set_end_time() {
  var li = document.createElement('li');
  li.className = 'list-group-item d-flex flex-row';
  li.appendChild(ruleIndexDiv($('ul#rule-list li').length+1));
  li.appendChild(ruleNameDiv('set_end_time'));
  li.appendChild(targetFieldDiv());
  li.appendChild(startTimeDiv());
  li.appendChild(durationDiv());
  li.appendChild(helpItemDiv('https://hl7-transform.readthedocs.io/en/latest/mapping.html#hl7_transform.operations.SetEndTime'));
  li.appendChild(deleteItemDiv());
  $('#rule-list').append(li);
  return li;
}

function addEmptyRule(name) {
  if (supported_rules.hasOwnProperty(name)) {
    var li = supported_rules[name]();
    return li;
  }
  else {
    alert('Unknown rule ' + name);
    return null;
  }
}

function ruleIndexDiv(index) {
  var div = document.createElement('div');
  div.className = 'p-2';
  div.innerHTML = index;
  return div;
}

function ruleNameDiv(name) {
  var div = document.createElement('div');
  div.className = 'p-2 flex-nowrap';
  div.setAttribute('name', 'rule-name');
  div.innerHTML = name;
  return div;
}

function textInputDiv(name, placeholder) {
  var div = document.createElement('div');
  div.className = 'p-2';
  var input = document.createElement('input');
  input.type = 'text';
  input.className = 'form-control';
  input.setAttribute('placeholder', placeholder);
  input.setAttribute('name', name);
  div.appendChild(input);
  return div;
}

function targetFieldDiv() {
  return textInputDiv('rule-target-field', 'Target field');
}

function sourceFieldDiv() {
  return textInputDiv('rule-source-field', 'Source field');
}

function startTimeDiv() {
  return textInputDiv('rule-start-time-field', 'Start time field');
}

function durationDiv() {
  return textInputDiv('rule-duration-field', 'Duration field');
}

function operandDiv() {
  return textInputDiv('rule-operand-field', 'Operand field');
}

function valueTypeDiv() {
  return selectDiv('rule-value-type-field', ['int', 'str']);
}

function separatorDiv() {
  return textInputDiv('rule-separator', 'Separator');
}

function selectDiv(name, options) {
  var div = document.createElement('div');
  div.className = 'p-2';
  var input = document.createElement('select');
  input.className = 'form-control';
  input.setAttribute('name', name);
  options.forEach(function(item, index){
    var option = document.createElement('option');
    option.innerHTML = item;
    input.appendChild(option);
  });
  div.appendChild(input);
  return div;
}

function deleteItemDiv() {
  var div = document.createElement('div');
  div.className = 'p-2';
  div.innerHTML = '<a href="#" class="icon-delete"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-trash" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/><path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4L4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/></svg></a>';
  return div;
}

function helpItemDiv(link) {
  var div = document.createElement('div');
  div.className = 'ml-auto p-2';
  div.innerHTML = '<a href="' + link + '" target="help"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-question-square" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M14 1H2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/><path d="M5.25 6.033h1.32c0-.781.458-1.384 1.36-1.384.685 0 1.313.343 1.313 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.007.463h1.307v-.355c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.326 0-2.786.647-2.754 2.533zm1.562 5.516c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/></svg></a>';
  return div;
}

function valueDiv() {
  var div = document.createElement('div');
  div.className = 'p-2';
  var input = document.createElement('input');
  input.type = 'text';
  input.className = 'form-control';
  input.setAttribute('placeholder', 'Value');
  input.setAttribute('name', 'rule-value');
  div.appendChild(input);
  return div;
}
