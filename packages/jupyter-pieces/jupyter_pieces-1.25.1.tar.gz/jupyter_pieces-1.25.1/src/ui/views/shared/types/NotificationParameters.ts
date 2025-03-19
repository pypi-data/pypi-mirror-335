export enum NotificationActionTypeEnum {
  OPEN_LINK = 'OPEN_LINK',
}

export type NotificationActionTypeToParams = {
  [NotificationActionTypeEnum.OPEN_LINK]: { url: string };
};

export type NotificationAction<T extends NotificationActionTypeEnum> = {
  type: T;
  params: NotificationActionTypeToParams[T];
  title: string;
};

export type NotificationParameters = {
  message: string;
  title?: string;
  type: 'info' | 'error' | 'warn';
  actions?: NotificationAction<NotificationActionTypeEnum>[];
};
