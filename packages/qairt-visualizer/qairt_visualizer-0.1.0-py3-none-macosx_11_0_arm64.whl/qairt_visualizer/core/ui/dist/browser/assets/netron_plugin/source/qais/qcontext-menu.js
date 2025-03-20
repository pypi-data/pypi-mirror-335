/*
* =============================================================================
*
*  Copyright (c) 2023-2024 Qualcomm Technologies, Inc.
*  All Rights Reserved.
*  Confidential and Proprietary - Qualcomm Technologies, Inc.
*
* ==============================================================================
*/

import * as qcontrol from './qcontrol.js';

const qcontextMenu = {};

qcontextMenu.init = class {
  static contextMenuList = {};

  static updateContextMenu(data) {
    this.contextMenuList = data;
    if (!Object.keys(this.contextMenuList).length) {
      this.hidePrevContextMenuButton(false, true);
    }
  }

  static escapePeriods(str) {
    return str.replace(/\./g, '\\.');
  }

  static addContexMenuButton(nodeId) {
    if (!Object.keys(this.contextMenuList).length) {
      return;
    }

    const nodeMenuId = nodeId + '-menu';
    const nodeElement = document.getElementById(nodeId);
    const nodeMenuSelector = this.escapePeriods('#' + nodeMenuId);
    const nodeMenu = nodeElement.querySelector(nodeMenuSelector);

    this.hidePrevContextMenuButton(nodeMenuId, false);  // hide the last selected nodes context menu button

    if (nodeMenu !== null) {
      nodeMenu.style.display = 'block';
      nodeMenu.setAttribute('data-node-contex-menu', 'true');
      return;
    }

    const menuContainer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    menuContainer.id = nodeMenuId;
    menuContainer.setAttribute('viewBox', '0 0 24 24');
    menuContainer.setAttribute('data-node-contex-menu', 'true');

    const menu = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    menu.setAttribute('d', "M11 16h-2v-2h2v2zM11 12h-2v-2h2v2zM11 8h-2v-2h2v2z");
    menu.style.fill = 'white';  
    menu.style.transform = `translate(${nodeElement.getBBox().width + 2 + 'px'}, -2px)`;

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', 10);
    circle.setAttribute('cy', 10);
    circle.setAttribute('r', 10);
    circle.setAttribute('fill', 'rgb(40, 62, 249)');
    circle.style.transform = `translate(${nodeElement.getBBox().width + 2 + 'px'}, -1px)`;

    menuContainer.appendChild(circle);
    menuContainer.appendChild(menu);
    nodeElement.appendChild(menuContainer);
  }

  static hidePrevContextMenuButton(nodeMenuId, isOutputNodeClicked = false) {
    const lastNodeMenuButton = document.querySelector("[data-node-contex-menu=true]");
    if (lastNodeMenuButton) {
      if (isOutputNodeClicked || lastNodeMenuButton.id !== nodeMenuId) {
        lastNodeMenuButton.style.display = 'none';
        lastNodeMenuButton.setAttribute('data-node-contex-menu', 'false');
      }
    }
  }

  static toggleContextMenu(nodeRect) {
    if (!this.contextMenuList) {
      return;
    }

    const menuContainer = document.getElementById('context-menu-container');
    const currentHighlitedNode = document.querySelector("[data-node-contex-menu=true]");

    if (menuContainer) {
      if (menuContainer.style.visibility === 'visible') {
        menuContainer.style.visibility = 'hidden';
      } else {
        this.updateContextMenuPosition(menuContainer, nodeRect);
        menuContainer.style.visibility = 'visible';
      }
    } else {
      this.createContextMenu(nodeRect);
    }

    currentHighlitedNode.style.opacity = '0.7';
  }

  static updateContextMenuPosition(menuContainer, nodeRect) {
    const nearToSideDistance = menuContainer.childElementCount == 3 ? 120 : 80;
    const menuSpacing = 20;

    if (window.innerHeight < nodeRect.top + nearToSideDistance) {
      menuContainer.style.top = `${window.innerHeight - menuContainer.offsetHeight}px`;
    } else {
      menuContainer.style.top = `${nodeRect.top + menuSpacing}px`;
    }

    if (window.innerWidth < nodeRect.left + nearToSideDistance) {
      menuContainer.style.left = `${window.innerWidth - menuContainer.offsetWidth}px`;
    } else {
      menuContainer.style.left = `${nodeRect.left + menuSpacing}px`;
    }
  }

  static highlightClickHandler(panelToHighlight) {
    this.hideContextMenu();
    const currentHighlitedNode = document.querySelector("[data-node-contex-menu=true]");
    const nodeId = currentHighlitedNode.id.replace('-menu', '');
    qcontrol.messageEmitter.emitMessage('property_request', { propertyType: 'node', nodeId: nodeId, panelToHighlight });
  }

  static createContextMenu(nodeRect) {
    if (!Object.keys(this.contextMenuList).length) {
      return;
    }

    const menuContainer = document.createElement('div');
    menuContainer.id = 'context-menu-container';
    menuContainer.setAttribute('class', 'context-menu-container');

    const menuItem = document.createElement('div');
    menuItem.setAttribute('class', 'context-menu-option');

    for (const menuOption in this.contextMenuList) {
      this.addContextMenuOption(menuContainer, menuItem, this.contextMenuList[menuOption].label, this.contextMenuList[menuOption].panelType);
    }

    menuContainer.style.position = 'absolute';
    if (nodeRect) {
      menuContainer.style.top = nodeRect.top + 20 + 'px';
      menuContainer.style.left = nodeRect.left + 'px';
    }
    document.body.appendChild(menuContainer);
  }


  static addContextMenuOption(menuContainer, menuItem, label, panelType) {
    const menuOption = menuItem.cloneNode(true);
    menuOption.innerText = label;
    menuOption.addEventListener('click', () => {
      this.highlightClickHandler(panelType);
    });
    menuContainer.appendChild(menuOption);
  }

  static removeContextMenu() {
    const menuContainer = document.getElementById('context-menu-container');
    if (menuContainer) {
      menuContainer.remove();
    }
  }

  static hideContextMenu() {
    const menuContainer = document.getElementById('context-menu-container');
    if (menuContainer) {
      menuContainer.style.visibility = 'hidden';
    }

    const currentHighlitedNode = document.querySelector("[data-node-contex-menu=true]");
    if (currentHighlitedNode) {
      currentHighlitedNode.style.opacity = '1';
    }
  }

  static graphClickListenerForContextMenu(event) {
    event.stopImmediatePropagation();
    const lastHighlitedNode = document.querySelector("[data-node-contex-menu=true]");
    if (!lastHighlitedNode) {
      return;
    }
    const clickX = event.clientX;
    const clickY = event.clientY;
    const menuButtonRect = lastHighlitedNode.getBoundingClientRect();
    const isMenuClicked = clickX >= menuButtonRect.left && clickX <= menuButtonRect.right && clickY >= menuButtonRect.top && clickY <= menuButtonRect.bottom;
    if (isMenuClicked) {
      this.toggleContextMenu(menuButtonRect);
    } else {
      this.hideContextMenu();
    }
  }
};

export const init = qcontextMenu.init;
