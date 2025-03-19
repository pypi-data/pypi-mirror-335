function adjustInputWidth(input) {
  input.style.width = 'auto';
  if (input.type === 'number') {
    delta = 30;
  } else {
    delta = 3;
  }
  input.style.width = `${input.scrollWidth + delta}px`;
}

function formInputHandle() {
  schemaForm.querySelectorAll('input[type="text"], input[type="number"]').forEach(input => {
    if (! inputHandlers.includes(input)) {
      val = input.placeholder;
      if (val) {
        size = Math.max(val.length, 2)
        if (input.type== 'number') {
          size += 2;
        }
      } else {
        size = 12;
      }
      if (input.value) {
        size = 2;
      }
      input.setAttribute('size', size);
      setTimeout(() => adjustInputWidth(input), 1);
      input.addEventListener('input', () => adjustInputWidth(input));
      inputHandlers.push(input);
    }
  });
}

function extractKeysAndPlaceholders(obj, formoptions, prefix = '') {
    let result = [];
  
    for (let key in obj.properties) {
      k = prefix ? `${prefix}.${key}` : key;
      if (obj.properties[key].type === 'object' && obj.properties[key].properties) {
        result = result.concat(extractKeysAndPlaceholders(obj.properties[key], formoptions, k));
      } else {
        if (formoptions[k]) {
          foptions = formoptions[k];
        } else {
          foptions = {};
        }
        result.push({
          key: k,
          placeholder: obj.properties[key].example || null,
          ... foptions
        });
      }
    }
    return result;
}

function createSchemaForm(form, schema, onSubmit, schemaName) {
  if (schemaValues[schemaName]) {
    value = schemaValues[schemaName];
  } else {
    value = {};
  }
  if (schema && schema.schema_options) {
    schema_options = schema.schema_options;
  } else {
    schema_options = {};
  }
  if (schema && schema.properties && schema.properties.params && schema.properties.params.schema_options) {
    schema_params_options = schema.properties.params.schema_options;
  } else {
    schema_params_options = {};
  }

  formoptions = {};
  if (schema_options && schema_options.form) {
    formoptions = schema.schema_options.form;
  } else if (schema_params_options && schema_params_options.form) {
    for (let key in schema_params_options.form) {
      formoptions[`params.${key}`] = schema_params_options.form[key];
    }
  }
  formDesc = extractKeysAndPlaceholders(schema, formoptions);
  schemaForm = form[0];
  if (onSubmit != null) {
    if (schema_options && schema_options.batch_param) {
      schema.properties[schema_options.batch_param].required = true;
      if (!schema.properties.parallel) {
        schema.properties['parallel'] = {
          type: 'integer',
          default: 1,
          minimum: 1,
          maximum: 100,
          required: true,
          description: "nb parallel jobs"
        };
        schema.properties['delay'] = {
          type: 'integer',
          default: 10,
          minimum: 0,
          maximum: 600,
          required: true,
          description: "initial delay in s between jobs"
        };
        formDesc.push({
          key: 'parallel',
        });
        formDesc.push({
          key: 'delay',
        });
      }
      for (i = 0; i < formDesc.length; i++) {
        if (formDesc[i].key == schema_options.batch_param) {
          formDesc[i].type = 'textarea';
          formDesc[i].required = true;
        }
        if (formDesc[i].key == 'parallel') {
          formDesc[i].type = 'range';
          formDesc[i].indicator = true;
        }
        if (formDesc[i].key == 'delay') {
          formDesc[i].type = 'range';
          formDesc[i].indicator = true;
        }
      }
    }
    formDesc.push({
      type: 'submit',
      title: 'Run',
    });
  } else {
    if (schema_params_options && schema_params_options.batch_param) {
      schema.properties.params.properties[schema_params_options.batch_param].required = true;
      for (i = 0; i < formDesc.length; i++) {
        if (formDesc[i].key == 'params.' + schema_params_options.batch_param) {
          formDesc[i].type = 'textarea';
          formDesc[i].required = true;
        }
        if (formDesc[i].key == 'parallel') {
          formDesc[i].type = 'range';
          formDesc[i].indicator = true;
        }
        if (formDesc[i].key == 'delay') {
          formDesc[i].type = 'range';
          formDesc[i].indicator = true;
        }
      }
    }
  }
  form[0].classList.add('form-inline');
  jsform = form.jsonForm({
    schema: schema,
    onSubmit: onSubmit,
    form: formDesc,
    value: value,
    // params: {
    //     fieldHtmlClass: "input-small",
    // }
  });
  form[0].firstChild.classList.add('form-inline');
  form[0].querySelectorAll('._jsonform-array-addmore').forEach(btn => {
    btn.addEventListener('click', formInputHandle);
  });
  formInputHandle();

  form[0].querySelectorAll('textarea').forEach(txt => {
    txt.style.height = "0";  
    setTimeout(() => adjustTxtHeight(txt), 1);
    txt.setAttribute("spellcheck", "false");
    txt.addEventListener("input", () => adjustTxtHeight(txt));
  });

  form[0].addEventListener('input', () => {
    schemaValues[schemaName] = jsform.root.getFormValues();
    localStorage.setItem('schemaValues', JSON.stringify(schemaValues));
  });
  
  return jsform;
}
function adjustTxtHeight(txt) {
  if (txt.value.includes('\n')) {
    delta = 2;
  } else {
    delta = 0;
  }
  txt.style.height = "0";
  txt.style.height = `${txt.scrollHeight+delta}px`;
}
async function getSwaggerSpec() {
  const response = await fetch('/swagger.yaml');
  if (!response.ok) {
    return null;
  }
  const yamlText = await response.text();
  // Changed from yaml.parse to jsyaml.load because js-yaml exposes jsyaml
  return jsyaml.load(yamlText);
}
  
async function getPostParametersSchema() {
  const swaggerSpec = await getSwaggerSpec();
  const result = {};
  for (const path in swaggerSpec.paths) {
    const pathItem = swaggerSpec.paths[path];
    if (pathItem.post) {
      const postDef = pathItem.post;
      // Look for a parameter in the body with a schema property
      if (postDef.parameters && Array.isArray(postDef.parameters)) {
        const bodyParam = postDef.parameters.find(p => p.in === 'body' && p.schema);
        result[path] = bodyParam ? bodyParam.schema : null;
      } else {
        result[path] = null;
      }
    }
  }
  return result;
}

let schemaForm;
let inputHandlers = [];
let schemaValues = JSON.parse(localStorage.getItem('schemaValues')) || {};


