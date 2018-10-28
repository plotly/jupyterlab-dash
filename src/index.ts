import {
  ILayoutRestorer,
  JupyterLab, JupyterLabPlugin
} from '@jupyterlab/application';
//
// import {
//   JSONExt
// } from '@phosphor/coreutils';

import {
  Message
} from '@phosphor/messaging';

// import {
//   InstanceTracker
// } from '@jupyterlab/apputils';

import {
  INotebookTracker, NotebookPanel
} from '@jupyterlab/notebook';

import {
  Widget
} from '@phosphor/widgets';

import {
    KernelMessage, Kernel
} from "@jupyterlab/services";


import '../style/index.css';

/**
 * An xckd comic viewer.
 */
class DashIFrameWidget extends Widget {
  /**
   * Construct a new DashIFrameWidget.
   */
  constructor(uid: string, url: string) {
    super();

    this.id = uid;
    this.url = url;
    this.title.label = 'Dash';
    this.title.closable = true;
    this.addClass('jp-dashWidget');

    // Add jp-IFrame class to keep drag events from being lost to the iframe
    // See https://github.com/phosphorjs/phosphor/issues/305
    // See https://github.com/jupyterlab/jupyterlab/blob/master/packages/apputils/style/iframe.css#L17-L35
    this.addClass('jp-IFrame');

    let iframeElement = document.createElement('iframe');
    iframeElement.setAttribute('baseURI', '');
    this.iframe = iframeElement;
    this.iframe.src = url;
    this.iframe.id = 'iframe-' + this.id;

    this.node.appendChild(this.iframe);
  }

  /**
   * The image element associated with the widget.
   */
  readonly iframe: HTMLIFrameElement;

  /**
   * URL
   */
  readonly url: string;

  /**
   * Handle update requests for the widget.
   */
  onUpdateRequest(msg: Message): void {
    console.log('onUpdateRequest');
    // (document.getElementById(this.iframe.id) as HTMLIFrameElement).contentWindow.location.reload();
    let delay = new Promise(resolve => setTimeout(resolve, 100));
    delay.then(() => {
      this.iframe.src += '';
    });

    // .contentWindow.location.reload();
    // this.iframe.contentWindow.location.reload();
  }
};

interface DashMessageData {
  type:    string;
  uid:     string;
  url:     string;
}

/**
 * Activate the xckd widget extension.
 */
function activate(app: JupyterLab,
                  restorer: ILayoutRestorer,
                  notebooks: INotebookTracker) {

  console.log('JupyterLab extension jupyterlab_dash is activated!');

  // Declare a widget variable
  // let widgets: { [uid: string]: DashIFrameWidget; } = { };
  let widgets = new Map<string, DashIFrameWidget>();

  // Watch notebook creation
  notebooks.widgetAdded.connect(( sender, nbPanel: NotebookPanel ) => {
    console.log('Notebook added!');
    const session = nbPanel.session;
    session.ready.then(() =>  {
      console.log("Notebook session ready");
      let kernel = session.kernel;
      kernel.ready.then(() => {
        console.log("Notebook kernel ready");

        // Register comm
        kernel.registerCommTarget('dash_viewer',
            (comm: Kernel.IComm, msg: KernelMessage.ICommOpenMsg) => {
              console.log('dash_viewer comm opened!');
              comm.onMsg = (msg: KernelMessage.ICommMsgMsg) => {
                console.log("dash_viewer comm message received");
                console.log(msg);
                let msgData = msg.content.data as unknown as DashMessageData;
                console.log(msgData.type);
                if (msgData.type === 'show') {

                  let widget: DashIFrameWidget;
                  if (!widgets.has(msgData.uid)) {
                    // Create a new widget
                    console.log('Create new widget');
                    widget = new DashIFrameWidget(msgData.uid, msgData.url);
                    widget.update();
                    widgets.set(msgData.uid, widget);

                    // Add instance tracker stuff
                  } else {
                    console.log('Found existing widget');
                    widget = widgets.get(msgData.uid);
                  }

                  if (!widget.isAttached) {
                    // Attach the widget to the main work area
                    // if it's not there
                    console.log('Widget was not attached, adding to main area');
                    app.shell.addToMainArea(widget);
                  } else {
                    // Refresh the widget
                    console.log('Widget already, updating');
                    widget.update();
                  }

                  // Activate the widget
                  app.shell.activateById(widget.id);
                }
              };

              comm.onClose = (msg: KernelMessage.ICommCloseMsg) => {
                console.log('dash_viewer comm message closed');
                console.log(msg);
              };
        });
      })
    })
  });

  //
  // // Track and restore the widget state
  // let tracker = new InstanceTracker<Widget>({ namespace: 'xkcd' });
  // restorer.restore(tracker, {
  //   command,
  //   args: () => JSONExt.emptyObject,
  //   name: () => 'plotly-dash'
  // });
};

/**
 * Initialization data for the jupyterlab_dash extension.
 */
const extension: JupyterLabPlugin<void> = {
  id: 'jupyterlab_dash',
  autoStart: true,
  requires: [ILayoutRestorer, INotebookTracker],
  activate: activate
};

export default extension;
