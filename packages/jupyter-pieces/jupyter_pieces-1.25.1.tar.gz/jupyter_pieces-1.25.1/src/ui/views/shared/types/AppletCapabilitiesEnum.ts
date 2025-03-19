export enum AppletCapabilities {
  insertAtCursor = 0b0000_0001, // 1
  askCopilot = 0b0000_0010, // 2
  acceptChanges = 0b0000_0100, // 4
  displayNotification = 0b0000_1000, // 8
  persistState = 0b0001_0000, // 16
  previewAsset = 0b0010_0000, // 32
  openSettings = 0b0100_0000, // 64
  searchAssets = 0b1000_0000, // 128
  launchPos = 0b0000_0001 << 8, // 256
  installPos = 0b0000_0010 << 8, // 512
  corsProxy = 0b0000_0100 << 8, // 1024
  setTheme = 0b0000_1000 << 8, // 2048
  addToContext = 0b0001_0000 << 8, // 4092
  copyToClipboard = 0b0010_0000 << 8, // 8192
  loaded = 0b0100_0000 << 8, // 16384
  pasteFromClipboard = 0b1000_0000 << 8, // 32768
  runInTerminal = 0b0000_0001 << 16, // 65536
  focusSearch = 0b0000_0010 << 16, // 131072
  focusCopilotConversation = 0b0000_0100 << 16, // 262144
  SearchResultAction = 0b0000_1000 << 16, // 524,288
  EditAsset = 0b0001_0000 << 16, // 1_048_576
  All = 0b00011111_11111111_11111111, // 2_097_151
}
