/*
* =============================================================================
*
*  Copyright (c) 2023-2024 Qualcomm Technologies, Inc.
*  All Rights Reserved.
*  Confidential and Proprietary - Qualcomm Technologies, Inc.
*
* ==============================================================================
*/

import * as qbin from './qbin.js';

const qnn = {};

qnn.ModelFactory = class {

  //matching for model type
  match(context) {
    const identifier = context.identifier;
    const extension = identifier.split('.').pop().toLowerCase();
    const obj = context.peek('json');
    if (extension === 'json') {
      if (obj['model.bin'] && obj['model.cpp']) {
        return true;
      }
    }
    return false;
  }

  //opens the QNN model
  open(context) {
    return qnn.Metadata.open(context).then(async (metadata) => {
      if (window.__view__.binFile) {

        const qtar = new qbin.reader();
        const binParser = new qbin.parser();
        await qtar.readFile(window.__view__.binFile);
        window.__view__.binFileMap = new Map();

        const model = context.peek('json');
        const tensors = Object.entries(model.graph.tensors)
        for (let i = 0; i < tensors.length; i++) {
          const tensor = tensors[i];
          const tensorData = tensor[1];
          const type = tensorData['type'];
          if (type === TypeOfArgument.STATIC || type === TypeOfArgument.QNN_TENSOR_TYPE_STATIC) {

            const blob = qtar.getFileBlob(tensor[0].trim() + '.raw');
            const dataType = findDataType(tensorData['data_type']);
            binParser.dataType = dataType;
            const weights = await binParser.convertBlobToArray(blob);
            window.__view__.binFileMap.set(tensor[0], weights);
          }
        }
      }
      return new qnn.Model(metadata, context.peek('json'));
    });
  }

};


qnn.Model = class {
  constructor(metadata, model) {

    this._graphs = [];
    this._model = model;
    this._graphs.push(new qnn.Graph(metadata, model));
  }

  get converter_command() {
    return this._model.converter_command;
  }

  get copyright() {
    return this._model.copyright_str || 'N/A';
  }

  get format() {
    return 'QNN Model';
  }

  get graphs() {
    return this._graphs;
  }

  get model_cpp() {
    return this._model['model.cpp'] || 'N/A';
  }

  get model_bin() {
    return this._model['model.bin'] || 'N/A';
  }
  get op_types() {
    return this._model.op_types.toString().replace(/,/g, ', \n');
  }

  get total_param() {
    return this._model['Total parameters'];
  }

  get total_mac() {
    return this._model['Total MACs per inference'];
  }
};

//enums for the type of argument
const TypeOfArgument = {
  INPUT: 0,
  STATIC: 4,
  OUTPUT: 1,
  NATIVE: 3,
  QNN_TENSOR_TYPE_APP_WRITE: 'QNN_TENSOR_TYPE_APP_WRITE',
  QNN_TENSOR_TYPE_STATIC: 'QNN_TENSOR_TYPE_STATIC',
  QNN_TENSOR_TYPE_APP_READ: 'QNN_TENSOR_TYPE_APP_READ',
  QNN_TENSOR_TYPE_NATIVE: 'QNN_TENSOR_TYPE_NATIVE'
};

//enums for the data Type
const DataType = {
  INT8: 8,
  INT16: 22,
  INT32: 50,
  INT64: 100,

  UINT8: 264,
  UINT16: 278,
  UINT32: 306,
  UINT64: 356,

  FLOAT16: 534,
  FLOAT32: 562,

  SFIXEDPOINT8: 776,
  SFIXEDPOINT16: 790,
  SFIXEDPOINT32: 818,

  UFIXEDPOINT8: 1032,
  UFIXEDPOINT16: 1046,
  UFIXEDPOINT32: 1074
};

//returns the data type of the graph
function findDataType(dataType) {
  switch (dataType) {
    case DataType.INT8:
    case 'QNN_DATATYPE_INT_8':
      return 'INT8';
    case DataType.INT16:
    case 'QNN_DATATYPE_INT_16':
      return 'INT16';
    case DataType.INT32:
    case 'QNN_DATATYPE_INT_32':
      return 'INT32';
    case DataType.INT64:
    case 'QNN_DATATYPE_INT_64':
      return 'INT64';
    case DataType.UINT8:
    case 'QNN_DATATYPE_UINT_8':
      return 'UINT8';
    case DataType.UINT16:
    case 'QNN_DATATYPE_UINT_16':
      return 'UINT16';
    case DataType.UINT32:
    case 'QNN_DATATYPE_UINT_32':
      return 'UINT32';
    case DataType.UINT64:
    case 'QNN_DATATYPE_UINT_64':
      return 'UINT64';
    case DataType.FLOAT16:
    case 'QNN_DATATYPE_FLOAT_16':
      return 'FLOAT16';
    case DataType.FLOAT32:
    case 'QNN_DATATYPE_FLOAT_32':
      return 'FLOAT32';
    case DataType.SFIXEDPOINT8:
    case 'QNN_DATATYPE_SFIXED_POINT_8':
      return 'SFIXEDPOINT8';
    case DataType.SFIXEDPOINT16:
    case 'QNN_DATATYPE_SFIXED_POINT_16':
      return 'SFIXEDPOINT16';
    case DataType.SFIXEDPOINT32:
    case 'QNN_DATATYPE_SFIXED_POINT_32':
      return 'SFIXEDPOINT32';
    case DataType.UFIXEDPOINT8:
    case 'QNN_DATATYPE_UFIXED_POINT_8':
      return 'UFIXEDPOINT8';
    case DataType.UFIXEDPOINT16:
    case 'QNN_DATATYPE_UFIXED_POINT_16':
      return 'UFIXEDPOINT16';
    case DataType.UFIXEDPOINT32:
    case 'QNN_DATATYPE_UFIXED_POINT_32':
      return 'UFIXEDPOINT32';
  }
}


// creates a map of the tensor names as keys and the corresponding argument as the value
//this method also checks to see what type of argument it is (input,output, or internal) and adds it
//to the corresponding list using IOSetter
qnn.ValueMapper = class {

  constructor(iosetter, tensors) {

    this._valueMap = new Map();

    for (let i = 0; i < tensors.length; i++) {
      const tensor = tensors[i];
      const tensorData =  tensor[1];

      const dataType = findDataType(tensorData['data_type']);
      const shape = new qnn.TensorShape(tensorData['dims']);
      let scale_offset = '';
      if (tensorData['quant_params']['scale_offset']) {
        scale_offset = JSON.stringify(tensorData['quant_params']['scale_offset']);
      } else {
        scale_offset = JSON.stringify(tensorData['quant_params']['axis_scale_offset']['scale_offsets']);
      }
      const encoding = tensorData['quant_params']['encoding'];
      const axis_format = tensorData['axis_format'];
      const inputType = new qnn.TensorType(dataType + '\n Scale_Offsets:' + scale_offset + '\n Encoding:' + encoding + '\n Axis_Format:' + axis_format + '\n', shape);
      const type = tensorData['type'];
      let value = new qnn.Value(tensor[0], inputType);
      switch (type) {
        case TypeOfArgument.INPUT:
        case TypeOfArgument.QNN_TENSOR_TYPE_APP_WRITE:
          iosetter.addInput(value);
          break;
        case TypeOfArgument.STATIC:
        case TypeOfArgument.QNN_TENSOR_TYPE_STATIC:
          if (window.__view__.binFile) {
            const weights = window.__view__.binFileMap.get(tensor[0])
            value = new qnn.Value(tensor[0], inputType, new qnn.Tensor(inputType, weights));
            iosetter.addInput(value);
          }
          break;
        case TypeOfArgument.OUTPUT:
        case TypeOfArgument.QNN_TENSOR_TYPE_APP_READ:
          iosetter.addOutput(value);
          break;
        case TypeOfArgument.NATIVE:
        case TypeOfArgument.QNN_TENSOR_TYPE_NATIVE:
          break;

      }
      this._valueMap.set(tensor[0], value);
    }

  }

  get valueMap() {
    return this._valueMap;
  }

};

qnn.IOSetter = class {

  constructor() {
    this._inputValues = [];
    this._outputValues = [];

  }

  addInput(value) {
    this._inputValues.push(value);
  }

  addOutput(value) {
    this._outputValues.push(value);
  }

  get inputs() {
    return this._inputValues;
  }

  get outputs() {
    return this._outputValues;
  }


};

qnn.Attribute = class {

  constructor(name, value) {
    this._name = name;
    this._value = value;
    this._visible = true;
  }

  get name() {
    return this._name;
  }

  get value() {
    return this._value;
  }

  get visible() {
    return this._visible == false ? false : true;
  }
};
/*
    * OPEN_SOURCE_START
    * The following code is derived from the netron open source project in order to setup the graph object as needed
    * for the QNN Graph use case
    * Note: Minor modifications done to align with QNN requirements
    * Project Link: https://github.com/lutzroeder/netron/
    * Project License: MIT License
*/
//creates a Graph Object for a QNN Network
qnn.Graph = class {

  constructor(metadata, model) {

    this._nodes = [];
    this._inputs = [];
    this._outputs = [];

    //create argument object for tensors
    const ioSetter = new qnn.IOSetter();
    const graphValueMapper = new qnn.ValueMapper(ioSetter, Object.entries(model.graph.tensors));
    const graphValueMap = graphValueMapper.valueMap;

    //get list of the arguments for the absolute inputs an outputs of the graph
    const inputValues = ioSetter.inputs;
    const outputValues = ioSetter.outputs;

    for (const input of inputValues) {
      if (!input.initializer) {
        this._inputs.push(new qnn.Argument(input.name, [ input ]));
      }
    }
    for (const output of outputValues) {
        if (!output.initializer) {
          this._outputs.push(new qnn.Argument(output.name, [ output ]));
        }
    }

    //create the internal nodes
    const nodeMap = Object.entries(model.graph.nodes);

    //create all nodes
    for (let k = 0; k < nodeMap.length; k++) {
      const node = nodeMap[k];
      const nodeName = node[0];
      const nodeType = node[1].type;
      const inputNames = node[1]['input_names'];
      const outputNames = node[1]['output_names'];
      const tensorParams = node[1]['tensor_params'];

      //input parameters for the node
      const nodeInputPars = [];
      for (let m = 0; m < inputNames.length; m++) {
        const nodeInputArgs = [];
        nodeInputArgs.push(graphValueMap.get(inputNames[m]));
        nodeInputPars.push(new qnn.Argument(inputNames[m], nodeInputArgs));
      }

      //output parameters for the node
      const nodeOutputPars = [];
      for (let l = 0; l < outputNames.length; l++) {
        const nodeOutputArgs = [];
        nodeOutputArgs.push(graphValueMap.get(outputNames[l]));
        nodeOutputPars.push(new qnn.Argument(outputNames[l], nodeOutputArgs));

      }

      //put in attributes if there are any for the node
      const tensorParamsMap = Object.entries(tensorParams);
      const attributeList = [];
      for (let j = 0; j < tensorParamsMap.length; j++) {
        const param = tensorParamsMap[j][0];
        const attributes = tensorParamsMap[j][1];
        const attributeArgumentMap = Object.entries(attributes);
        const attributenum = attributeArgumentMap[0][1]['type'];
        const scale = 'Scale: ' + attributeArgumentMap[0][1]['quant_params']['scale_offset']['scale'];
        const offset = 'Offset: ' + attributeArgumentMap[0][1]['quant_params']['scale_offset']['offset'];
        let attributeType = '';
        switch (attributenum) {
          case TypeOfArgument.INPUT:
          case TypeOfArgument.QNN_TENSOR_TYPE_APP_WRITE:
            attributeType = 'Type: INPUT ';
            break;
          case TypeOfArgument.STATIC:
          case TypeOfArgument.QNN_TENSOR_TYPE_STATIC:
            attributeType = 'Type: STATIC';
            break;
          case TypeOfArgument.OUTPUT:
          case TypeOfArgument.QNN_TENSOR_TYPE_APP_READ:
            attributeType = 'Type: OUTPUT';
          case TypeOfArgument.NATIVE:
          case TypeOfArgument.QNN_TENSOR_TYPE_NATIVE:
            attributeType = 'Type: NATIVE';
            break;

        }

        const attributeDim = 'Dimension: ' + attributeArgumentMap[0][1]['dims'];
        const attributeData = 'Data: ' + attributeArgumentMap[0][1]['data'];

        const attParam = [];
        attParam.push(attributeType);
        attParam.push(attributeDim);
        attParam.push(attributeData);
        attParam.push(scale);
        attParam.push(offset);


        attributeList.push(new qnn.Attribute(param, attParam));

      }

      this._nodes.push(new qnn.Node(nodeInputPars, metadata, nodeName, nodeOutputPars, nodeType, attributeList));

    }

  }

  get name() {
    return this._name;
  }

  get type() {
    return '';
  }

  get inputs() {
    return this._inputs;
  }

  get outputs() {
    return this._outputs;
  }

  get nodes() {
    return this._nodes;
  }
  get csv() {
    return this._csvInfo;
  }

};

/* OPEN_SOURCE_END */

/*
    * OPEN_SOURCE_START
    * The following code is derived from the netron open source project in order to keep track of node information
    * in QNN Graph similiar to how netron does it
    * Project Link: https://github.com/lutzroeder/netron/
    * Project License: MIT License
*/

qnn.Node = class {

  constructor(inputs, metadata, name, outputs, type, params) {
    this._operator = '';
    this._chain = [];
    this._category = '';
    this._inputs = inputs;
    this._metadata = metadata;
    this._name = name;
    this._outputs = outputs;
    this._nodetype = type;
    this._attributes = params || null;
    this._type = {
      name: type,
      attributes: this._attributes,
      description: '',
      inputs: this._inputs,
      outputs: this._outputs,
      summary: '',
      category: this.metadata && this.metadata.category ? this.metadata.category : ''
    }
  }

  get operator() {
    return this._operator;
  }

  get name() {
    return this._name;
  }

  get domain() {
    return null;
  }

  get documentation() {
    return '';
  }

  get category() {
    return this._category;
  }

  get inputs() {
    return this._inputs;
  }

  get outputs() {
    return this._outputs;
  }

  get attributes() {
    return this._attributes;
  }

  get type() {
    return this._type;
  }

  get nodetype() {
    return this._nodetype;
  }

  get nodes() {
    return this._nodes;
  }
  get chain() {
    return this._chain;
  }

  get metadata() {
    return this._metadata.type(this._nodetype);
  }

};

/* OPEN_SOURCE_END */

qnn.Attribute = class {

  constructor(name, value) {
    this._name = name;
    this._value = value;
  }

  get name() {
    return this._name;
  }

  get value() {
    return this._value;
  }

  get visible() {
    return this._visible == false ? false : true;
  }
};

/*
    * OPEN_SOURCE_START
    * The following code is derived from the netron open source project in order to keep track of parameter information
    * as well as argument information in QNN Graph similar to how netron does it
    * Project Link: https://github.com/lutzroeder/netron/
    * Project License: MIT License
*/

qnn.Argument = class {

  constructor(name, value) {
    this._name = name;
    this._value = value;
  }

  get name() {
    return this._name;
  }

  get value() {
    return this._value;
  }
};


qnn.Value = class {

  constructor(name, type, initializer, value) {
    if (typeof name !== 'string') {
      throw new caffe.Error("Invalid value identifier '" + JSON.stringify(name) + "'.");
    }
    this._name = name;
    this._type = type || null;
    this._initializer = initializer || null;
    this._value = value;
  }

  get name() {
    return this._name;
  }

  get type() {
    return this._type;
  }

  get initializer() {
    return this._initializer;
  }

  get value() {
    return this._value;
}
};

/* OPEN_SOURCE_END */

/*
    * OPEN_SOURCE_START
    * The following code is derived from the netron open source project in order to keep track of tensor information
    * in QNN Graph similiar to how netron does it
    * Project Link: https://github.com/lutzroeder/netron/
    * Project License: MIT License
    * Note: There are a few minor modifications to accommodate for QNN-Netron use case
*/

qnn.Tensor = class {

  constructor(tensorInfo, data) {
    this._name = '';
    this._type = tensorInfo;
    this._kind = '';
    this._values = data;
    this._data = null;
  }

  get name() {
    return this._name;
  }

  get kind() {
    return this._kind;
  }

  get type() {
    return this._type;
  }

  get state() {
    return this._context().state;
  }

  get value() {
    let context = this._context();
    if (context.state) {
      return null;
    }
    context.limit = Number.MAX_SAFE_INTEGER;
    return this._decode(context, 0);
  }

  toString() {
    let context = this._context();
    if (context.state) {
      return '';
    }
    context.limit = 10000;
    let value = this._decode(context, 0);
    return JSON.stringify(value, null, 4);
  }

  _context() {
    let context = {};
    context.state = null;
    context.index = 0;
    context.count = 0;

    if (this._data == null) {
      context.state = this._values;
      return context;
    }

    context.dataType = this._type.dataType;
    context.shape = this._type.shape.dimensions;
    context.dimensions = this.type.shape.dimensions;
    return context;
  }

  _decode(context, dimension) {
    let shape = context.shape;
    if (shape.length == 0) {
      shape = [1];
    }
    let size = shape[dimension];
    let results = [];
    if (dimension == shape.length - 1) {
      for (let i = 0; i < size; i++) {
        if (context.count > context.limit) {
          results.push('...');
          return results;
        }
        switch (context.dataType) {
          case 'float16':
            results.push(context.data.getFloat16(context.index, true));
            context.index += 2;
            context.count++;
            break;
          case 'float32':
            results.push(context.data.getFloat32(context.index, true));
            context.index += 4;
            context.count++;
            break;
          case 'quint8':
            results.push(context.data.getUint8(context.index));
            context.index += 1;
            context.count++;
            break;
          case 'qint16':
            results.push(context.data.getInt16(context.index, true));
            context.index += 2;
            context.count++;
            break;
          case 'int32':
            results.push(context.data.getInt32(context.index, true));
            context.index += 4;
            context.count++;
            break;
          case 'boolean':
            results.push(context.data.getInt8(context.index));
            context.index += 1;
            context.count++;
            break;
          default:
            break;
        }
      }
    }
    else {
      for (let j = 0; j < size; j++) {
        if (context.count > context.limit) {
          results.push('...');
          return results;
        }
        results.push(this._decode(context, dimension + 1));
      }
    }
    if (context.shape.length == 0) {
      return results[0];
    }
    return results;
  }

  get kind() {
    return null;
  }

  get values() {
    return this._values;
  }

  /* OPEN_SOURCE_END */

};

/*
    * OPEN_SOURCE_START
    * The following code is derived from the netron open source project in order to keep track of tensor type, shape,
    * model meta-data, and error throwing for loading a QNN model
    * Project Link: https://github.com/lutzroeder/netron/
    * Project License: MIT License
    * Note: There are a few minor modifications to accommodate for QNN-Netron use case
*/

qnn.TensorType = class {

  constructor(dataType, shape) {
    this._dataType = dataType;
    this._shape = shape;
  }

  get dataType() {
    return this._dataType;
  }

  get shape() {
    return this._shape;
  }

  toString() {
    return (this.dataType || '?') + this._shape.toString();
  }
};


qnn.TensorShape = class {

  constructor(dimensions) {
    this._dimensions = dimensions;
  }

  get dimensions() {
    return this._dimensions;
  }

  toString() {
    if (!this._dimensions || this._dimensions.length == 0) {
      return '';
    }
    return '[' + this._dimensions.map((dimension) => dimension.toString()).join(',') + ']';
  }
};

qnn.Metadata = class {

  static open(context) {
    if (qnn.Metadata._metadata) {
      return Promise.resolve(qnn.Metadata._metadata);
    }
    return context.request('qais/qnn-metadata.json', 'utf-8', null).then((data) => {
      qnn.Metadata._metadata = new qnn.Metadata(data);
      return qnn.Metadata._metadata;
    }).catch(() => {
      qnn.Metadata._metadata = new qnn.Metadata(null);
      return qnn.Metadata._metadata;
    });
  }

  constructor(data) {
    this._map = new Map();
    this._attributeCache = {};
    if (data) {
      const metadata = JSON.parse(data);
      this._map = new Map(metadata.map((item) => [item.name, item]));
    }
  }

  type(name) {
    return this._map.get(name);
  }

  attribute(type, name) {
    let map = this._attributeCache[type];
    if (!map) {
      map = {};
      const schema = this.type(type);
      if (schema && schema.attributes && schema.attributes.length > 0) {
        for (const attribute of schema.attributes) {
          map[attribute.name] = attribute;
        }
      }
      this._attributeCache[type] = map;
    }
    return map[name] || null;
  }
};



qnn.Error = class extends Error {
  constructor(message) {
    super(message);
    this.name = 'Error loading QNN model.';
  }
};

export const ModelFactory = qnn.ModelFactory;
export const Tensor = qnn.Tensor;

/* OPEN_SOURCE_END */
