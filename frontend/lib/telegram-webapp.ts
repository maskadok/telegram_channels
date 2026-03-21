declare global {
  interface Window {
    Telegram?: {
      WebApp?: TelegramWebApp;
    };
  }
}

export interface TelegramWebAppThemeParams {
  bg_color?: string;
  text_color?: string;
  hint_color?: string;
  button_color?: string;
  button_text_color?: string;
  secondary_bg_color?: string;
}

export interface TelegramWebApp {
  initData?: string;
  initDataUnsafe?: Record<string, unknown>;
  colorScheme?: "light" | "dark";
  platform?: string;
  themeParams?: TelegramWebAppThemeParams;
  ready: () => void;
  expand: () => void;
}


//инициализация мини апп
export function getTelegramWebApp(): TelegramWebApp | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.Telegram?.WebApp ?? null;
}
