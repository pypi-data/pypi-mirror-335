/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable no-mixed-spaces-and-tabs */
import * as semver from 'semver';
import { v4 as uuidv4 } from 'uuid';
import getTheme from './theme';
import { showErrorView } from './errorView';
import PiecesOSUpdating from '../../modals/PiecesOSUpdating';
import ConnectorSingleton from '../../../connection/connectorSingleton';
import { launchRuntime } from '../../../actions/launchRuntime';

export abstract class Applet {
  protected iframe!: HTMLIFrameElement;
  protected tab!: HTMLDivElement;
  protected iframeId: string;
  protected static port = navigator.userAgent.toLowerCase().includes('linux')
    ? 5323
    : 1000;
  protected static minimumVersion = '11.0.0';
  protected static maximumVersion = '12.0.0';
  protected static migration: number;
  protected static schemaNumber = 0;
  static resolveLoading: () => void;
  static loadingPromise: Promise<void> = new Promise(
    (resolve) => (Applet.resolveLoading = resolve)
  );
  abstract getUrl(): Promise<URL>;
  static activeApplet: Applet;

  constructor(iframeId: string) {
    this.iframeId = iframeId;
  }

  async init(tab: HTMLDivElement) {
    this.tab = tab;
    this.connectionPoller();
    this.iframe = document.createElement('iframe');
    this.iframe.id = this.iframeId;
    this.iframe.name = this.iframeId;
    this.iframe.setAttribute(
      'style',
      'width: 100%; height: 100%; margin: 0px; overflow: hidden; border: none;'
    );
    this.iframe.setAttribute('allow', 'clipboard-read; clipboard-write;');
    this.tab.appendChild(this.iframe);
    this.setupThemeObserver();
    this.setIframeUrl(this.iframe);
  }

  protected setupThemeObserver() {
    const setTheme = () => {
      this.iframe.contentWindow?.postMessage(
        {
          type: 'setTheme',
          destination: 'webview',
          data: getTheme(),
        },
        '*'
      );
    };

    const observer = new MutationObserver(() => {
      setTheme();
    });
    observer.observe(document.body, { attributes: true });
  }

  static launchPos() {
    launchRuntime();
  }

  protected getNextMessageId() {
    return uuidv4();
  }

  async postToFrame(message: { [key: string]: any }) {
    message.destination = 'webview';
    await Applet.loadingPromise;
    this.iframe.contentWindow?.postMessage(message, '*');
  }

  protected async checkForConnection() {
    return ConnectorSingleton.getInstance()
      .wellKnownApi.getWellKnownHealth()
      .then(() => true)
      .catch(() => false);
  }

  protected async connectionPoller(): Promise<void> {
    const connected = await this.checkForConnection();

    let version = await ConnectorSingleton.getInstance()
      .wellKnownApi.getWellKnownVersion()
      .catch(() => null);

    version = version?.replace('-staging', '') ?? null;

    const isStaging = version?.includes('staging');
    const isDebug = version?.includes('debug');

    if (!isStaging && !isDebug) {
      // PiecesOS needs to update
      if (version && semver.lt(version, Applet.minimumVersion)) {
        this.tab.classList.remove('!hidden');
        this.iframe?.classList.add('!hidden');
        if (semver.lt(version, '9.0.2'))
          // PiecesOS does not have auto update capabilities previously 9.0.2
          showErrorView('Please Update PiecesOS!', this.tab);
        else new PiecesOSUpdating().open();
      }
      // extension needs to update
      if (version && semver.gte(version, Applet.maximumVersion)) {
        this.tab.classList.remove('!hidden');
        this.iframe.classList.add('!hidden');
        showErrorView(
          `The Pieces for Jupyter extension needs to be updated in order to work with PiecesOS version >= ${Applet.maximumVersion}`,
          this.tab
        );
      }
    }
    if (!connected) {
      this.iframe.classList.add('!hidden');
      if (!document.getElementById(`${this.tab.id}-error-view`))
        showErrorView('PiecesOS is not running!', this.tab);
    } else if (this.iframe.classList.contains('!hidden')) {
      document.getElementById(`${this.tab.id}-error-view`)?.remove();
      this.iframe.classList.remove('!hidden');
      this.setIframeUrl();
    }

    await new Promise((res) => setTimeout(res, 5000));
    return this.connectionPoller();
  }

  protected async setIframeUrl(iframe: HTMLIFrameElement | null = null) {
    if (iframe === null) {
      iframe = document.getElementById(
        this.iframeId
      ) as HTMLIFrameElement | null;
    }

    if (!iframe) throw new Error('Iframe is not present');
    const url = await this.getUrl();
    iframe.src = url.href;
    this.iframe.src = url.href;
  }
}
