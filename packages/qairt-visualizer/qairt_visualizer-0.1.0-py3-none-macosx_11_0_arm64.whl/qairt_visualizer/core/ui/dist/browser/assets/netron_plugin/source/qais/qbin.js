/*
* =============================================================================
*
*  Copyright (c) 2023-2024 Qualcomm Technologies, Inc.
*  All Rights Reserved.
*  Confidential and Proprietary - Qualcomm Technologies, Inc.
*
* ==============================================================================
*/
import * as float16 from './float16.js';

const qbin = {};

/**
 * OPEN_SOURCE_START
 * The following parts of code is derived from the tarballjs open source project used for extacting bin file
 * Note: Only a few methods has been picked as per our requirements
 * Project Link: https://github.com/ankitrohatgi/tarballjs/blob/master/tarball.js
 * Project License: https://github.com/ankitrohatgi/tarballjs/blob/master/LICENSE
 */

qbin.reader = class {
  constructor() {
    this.fileInfo = [];
  }

  readFile(file) {
    return new Promise((resolve, reject) => {
      let reader = new FileReader();
      reader.onload = (event) => {
        this.buffer = event.target.result;
        this.fileInfo = [];
        this._readFileInfo();
        resolve(this.fileInfo);
      };
      reader.readAsArrayBuffer(file);
    });
  }

  _readFileInfo() {
    this.fileInfo = [];
    let offset = 0;
    let file_size = 0;
    let file_name = "";
    let file_type = null;
    while (offset < this.buffer.byteLength - 512) {
      file_name = this._readFileName(offset);
      if (file_name.length == 0) {
        break;
      }
      file_type = this._readFileType(offset);
      file_size = this._readFileSize(offset);

      this.fileInfo.push({
        name: file_name,
        type: file_type,
        size: file_size,
        header_offset: offset
      });

      offset += (512 + 512 * Math.trunc(file_size / 512));
      if (file_size % 512) {
        offset += 512;
      }
    }
  }

  _readString(str_offset, size) {
    let strView = new Uint8Array(this.buffer, str_offset, size);
    let i = strView.indexOf(0);
    let td = new TextDecoder();
    return td.decode(strView.slice(0, i));
  }

  _readFileName(header_offset) {
    let name = this._readString(header_offset, 100);
    return name;
  }

  _readFileType(header_offset) {
    // offset: 156
    let typeView = new Uint8Array(this.buffer, header_offset + 156, 1);
    let typeStr = String.fromCharCode(typeView[0]);
    if (typeStr === '0') {
      return 'file';
    } else if (typeStr === '5') {
      return 'directory';
    } else {
      return typeStr;
    }
  }

  _readFileSize(header_offset) {
    // offset: 124
    let szView = new Uint8Array(this.buffer, header_offset + 124, 12);
    let szStr = "";
    for (let i = 0; i < 11; i++) {
      szStr += String.fromCharCode(szView[i]);
    }
    return parseInt(szStr, 8);
  }

  getFileBlob(file_name, mimetype) {
    let info = this.fileInfo.find(info => info.name == file_name);
    if (info) {
      return this._readFileBlob(info.header_offset + 512, info.size, mimetype);
    }
  }

  _readFileBlob(file_offset, size, mimetype) {
    let view = new Uint8Array(this.buffer, file_offset, size);
    let blob = new Blob([view], { type: mimetype });
    return blob;
  }

}

/* OPEN_SOURCE_END */

qbin.parser = class {

  async convertBlobToArray(blob) {
    try {
      const arrayBuffer = await this._readBlobAsArrayBuffer(blob);
      const convertedArray = this._convertArrayBufferToArray(arrayBuffer);
      return convertedArray;
    } catch (error) {
      console.error('Error converting blob to array:', error);
      return null;
    }
  }

  set dataType(dataType) {
    this._dataType = dataType;
  }

  _readBlobAsArrayBuffer(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsArrayBuffer(blob);
    });
  }

  /**
   * TODO : Add support for the INT64, UINT64 array buffer
   * Currently tested : FLOAT32, FLOAT16, SFIXEDPOINT32, SFIXEDPOINT8, UFIXEDPOINT8 datatypes
   */
  _convertArrayBufferToArray(buffer) {
    switch (this._dataType) {
      case 'FLOAT32':
        return new Float32Array(buffer);
      case 'FLOAT16':
        return new float16.Float16Array(buffer);
      case 'INT8':
        return new Int8Array(buffer);
      case 'INT16':
        return new Int16Array(buffer);
      case 'INT32':
        return new Int32Array(buffer);
      case 'UINT8':
        return new Uint8Array(buffer);
      case 'UINT16':
        return new Uint16Array(buffer);
      case 'UINT32':
        return new Uint32Array(buffer);
      case 'SFIXEDPOINT8':
        return new Uint8Array(buffer);
      case 'UFIXEDPOINT8':
        return new Uint8Array(buffer);
      case 'SFIXEDPOINT16':
        return new Uint16Array(buffer);
      case 'UFIXEDPOINT16':
        return new Uint16Array(buffer);
      case 'SFIXEDPOINT32':
        return new Uint32Array(buffer);
      case 'UFIXEDPOINT32':
        return new Uint32Array(buffer);
      default:
        throw new Error(`Invalid data type : ${this._dataType}`);
    }
  }

}

export const reader = qbin.reader;
export const parser = qbin.parser;
