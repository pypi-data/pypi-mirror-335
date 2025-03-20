/*
 * =============================================================================
 *
 *  Copyright (c) 2024 Qualcomm Technologies, Inc.
 *  All Rights Reserved.
 *  Confidential and Proprietary - Qualcomm Technologies, Inc.
 *
 * ==============================================================================
 */

import * as dagre from '../dagre.js';

addEventListener('message', ({ data }) => {
  data.parent = (v) => data.nodes.get(v).label.parent;
  dagre.layout(data, data._layout);
  delete data.parent;
  postMessage(data);
});
