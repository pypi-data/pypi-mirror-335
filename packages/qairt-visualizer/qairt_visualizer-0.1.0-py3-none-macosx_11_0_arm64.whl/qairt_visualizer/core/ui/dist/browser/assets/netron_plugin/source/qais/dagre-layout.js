/*
 * =============================================================================
 *
 *  Copyright (c) 2024 Qualcomm Technologies, Inc.
 *  All Rights Reserved.
 *  Confidential and Proprietary - Qualcomm Technologies, Inc.
 *
 * ==============================================================================
 */

function getDataForWorker(graph, layout) {
  const workerData = {
    nodes: new Map(),
    edges: new Map(),
    state: graph.state,
    _layout: layout,
  };

  graph.nodes.forEach((node, key) => {
    workerData.nodes.set(key, {
      v: node.v,
      label: {
        width: node.label.width,
        height: node.label.height,
        parent: graph.parent(node.v)
      },
    });
  });

  graph.edges.forEach((edge, key) => {
    workerData.edges.set(key, {
      v: edge.v,
      w: edge.w,
      label: {
        minlen: edge.label.minlen,
        weight: edge.label.weight,
        width: edge.label.width,
        height: edge.label.height,
        labeloffset: edge.label.labeloffset,
        labelpos: edge.label.labelpos
      },
    });
  });

  return workerData;
}

function applyLayoutToGraph(graph, layout) {
  layout.nodes.forEach((layoutNode, key) => {
    const { label } = graph.nodes.get(key);
    label.x = layoutNode.label.x;
    label.y = layoutNode.label.y;
  });
  layout.edges.forEach((layoutEdge, key) => {
    const { label } = graph.edges.get(key);
    label.x = layoutEdge.label.x;
    label.y = layoutEdge.label.y;
    label.points = layoutEdge.label.points;
  });
}

export default function dagreLayout(graph, layout) {
  return new Promise((resolve) => {
    const workerUrl = new URL('./dagre-layout.worker.js', import.meta.url);
    const worker = new Worker(workerUrl, { type: 'module' });
    worker.onmessage = ({ data }) => {
      applyLayoutToGraph(graph, data);
      worker.terminate();
      resolve();
    };

    const workerData = getDataForWorker(graph, layout);
    worker.postMessage(workerData);
  });
}
