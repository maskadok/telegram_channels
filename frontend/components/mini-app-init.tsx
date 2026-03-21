"use client";

import { useEffect, useState } from "react";

import { getTelegramWebApp } from "@/lib/telegram-webapp";


export function MiniAppInit() {
  const [isTelegram, setIsTelegram] = useState(false);

  useEffect(() => {
    //инициализация мини апп
    const webApp = getTelegramWebApp();

    if (!webApp) {
      return;
    }

    setIsTelegram(true);
    webApp.ready();
    webApp.expand();

    const theme = webApp.themeParams;
    if (theme?.bg_color) {
      document.documentElement.style.setProperty("--tg-bg", theme.bg_color);
    }
    if (theme?.secondary_bg_color) {
      document.documentElement.style.setProperty("--tg-surface", theme.secondary_bg_color);
    }
    if (theme?.text_color) {
      document.documentElement.style.setProperty("--tg-text", theme.text_color);
    }
    if (theme?.hint_color) {
      document.documentElement.style.setProperty("--tg-muted", theme.hint_color);
    }

    document.documentElement.dataset.telegram = "true";
  }, []);

  return (
    <div className="mini-app-badge" aria-live="polite">
      {isTelegram ? "Telegram Mini App" : "Browser Preview"}
    </div>
  );
}
