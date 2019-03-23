"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const application_1 = require("@jupyterlab/application");
const coreutils_1 = require("@jupyterlab/coreutils");
const notebook_1 = require("@jupyterlab/notebook");
const console_1 = require("@jupyterlab/console");
const widgets_1 = require("@phosphor/widgets");
require("../style/index.css");
class DashIFrameWidget extends widgets_1.Widget {
    /**
     * Construct a new DashIFrameWidget.
     */
    constructor(uid, port) {
        super();
        this.id = uid;
        this.title.label = 'Dash';
        this.title.closable = true;
        this.addClass('jp-dashWidget');
        // Add jp-IFrame class to keep drag events from being lost to the iframe
        // See https://github.com/phosphorjs/phosphor/issues/305
        // See https://github.com/jupyterlab/jupyterlab/blob/master/packages/apputils/style/iframe.css#L17-L35
        this.addClass('jp-IFrame');
        const baseUrl = coreutils_1.PageConfig.getBaseUrl();
        const serviceUrl = `${baseUrl}proxy/${port}`;
        const iframeElement = document.createElement('iframe');
        iframeElement.setAttribute('baseURI', serviceUrl);
        this.iframe = iframeElement;
        this.iframe.src = serviceUrl;
        this.iframe.id = 'iframe-' + this.id;
        this.node.appendChild(this.iframe);
    }
    /**
     * Handle update requests for the widget.
     */
    onUpdateRequest(msg) {
        this.iframe.src += '';
    }
}
/**
 * Activate the xckd widget extension.
 */
function activate(app, restorer, notebooks, consoles) {
    console.log('JupyterLab extension jupyterlab-dash is activated!');
    // Declare a widget variable
    let widgets = new Map();
    // Watch notebook creation
    notebooks.widgetAdded.connect((sender, nbPanel) => {
        console.log('Notebook added!');
        const session = nbPanel.session;
        session.ready.then(() => {
            console.log('Notebook session ready');
            let kernel = session.kernel;
            kernel.ready.then(() => {
                console.log('Notebook kernel ready');
                // Register comm
                registerCommTarget(kernel, widgets, app);
            });
        });
    });
    // Watch console creation
    consoles.widgetAdded.connect((sender, consolePanel) => {
        console.log('Console added!');
        const session = consolePanel.session;
        session.ready.then(() => {
            console.log('Console session ready');
            let kernel = session.kernel;
            kernel.ready.then(() => {
                console.log('Console kernel ready');
                // Register comm
                registerCommTarget(kernel, widgets, app);
            });
        });
    });
}
function registerCommTarget(kernel, widgets, app) {
    kernel.registerCommTarget('dash_viewer', (comm, msg) => {
        console.log('dash_viewer comm opened!');
        comm.onMsg = (msg) => {
            console.log('dash_viewer comm message received');
            console.log(msg);
            let msgData = msg.content.data;
            console.log(msgData.type);
            if (msgData.type === 'show') {
                let widget;
                if (!widgets.has(msgData.uid)) {
                    // Create a new widget
                    console.log('Create new widget');
                    widget = new DashIFrameWidget(msgData.uid, msgData.port);
                    widget.update();
                    widgets.set(msgData.uid, widget);
                    // Add instance tracker stuff
                }
                else {
                    console.log('Found existing widget');
                    widget = widgets.get(msgData.uid);
                }
                if (!widget.isAttached) {
                    // Attach the widget to the main work area
                    // if it's not there
                    console.log('Widget was not attached, adding to main area');
                    app.shell.addToMainArea(widget);
                    widget.update();
                }
                else {
                    // Refresh the widget
                    console.log('Widget already, updating');
                    widget.update();
                }
                // Activate the widget
                app.shell.activateById(widget.id);
            }
            else if (msgData.type === 'url_request') {
                const baseUrl = coreutils_1.PageConfig.getBaseUrl();
                comm.send({ type: 'url_response', url: baseUrl });
            }
        };
    });
}
/**
 * Initialization data for the jupyterlab-dash extension.
 */
const extension = {
    id: 'jupyterlab-dash',
    autoStart: true,
    requires: [application_1.ILayoutRestorer, notebook_1.INotebookTracker, console_1.IConsoleTracker],
    activate: activate
};
exports.default = extension;
