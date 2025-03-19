import { Notification } from '@jupyterlab/apputils';
import * as Sentry from '@sentry/browser';
import {
  NotificationAction,
  NotificationActionTypeEnum,
} from '../ui/views/shared/types/NotificationParameters';

export default class Notifications {
  private static instance: Notifications;

  private constructor() {
    /* */
  }

  public static getInstance(): Notifications {
    if (!Notifications.instance) {
      Notifications.instance = new Notifications();
    }

    return Notifications.instance;
  }

  public information({
    message,
    actions,
  }: {
    message: string;
    actions?: NotificationAction<NotificationActionTypeEnum>[];
  }) {
    Notification?.info(message, {
      autoClose: 3000,
      actions: actions?.reduce((acc, action) => {
        if (action.type === NotificationActionTypeEnum.OPEN_LINK) {
          acc.push({
            label: action.title,
            callback: (event: MouseEvent) => {
              window.open(action.params.url);
            },
          });
        }
        return acc;
      }, [] as { label: string; callback: (event: MouseEvent) => void }[]),
    });
  }

  public error({
    message,
    sendToSentry,
    actions,
  }: {
    message: string;
    sendToSentry?: boolean;
    actions?: NotificationAction<NotificationActionTypeEnum>[];
  }) {
    Notification.error(message, {
      autoClose: 3000,
      actions: actions?.reduce((acc, action) => {
        console.log('action');
        if (action.type === NotificationActionTypeEnum.OPEN_LINK) {
          acc.push({
            label: action.title,
            callback: (event: MouseEvent) => {
              window.open(action.params.url);
            },
          });
        }
        return acc;
      }, [] as { label: string; callback: (event: MouseEvent) => void }[]),
    });

    if (sendToSentry) {
      Sentry.captureException(message);
    }
  }
}
