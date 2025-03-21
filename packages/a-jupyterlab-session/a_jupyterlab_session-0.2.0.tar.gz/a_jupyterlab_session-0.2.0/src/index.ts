import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { IJupyterLiteSession } from 'a-jupyterlite-session';

/**
 * Initialization data for the a-jupyterlab-session extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'a-jupyterlab-session:plugin',
  autoStart: true,
  requires: [IJupyterLiteSession, IDefaultFileBrowser],
  activate: async (
    _app: JupyterFrontEnd,
    liteSession: IJupyterLiteSession,
    defaultFileBrowser: IDefaultFileBrowser
  ) => {
    console.log('JupyterLab extension a-jupyterlab-session is activated!');

    await defaultFileBrowser.model.cd(liteSession.sessionPath);
  }
};

export default plugin;
