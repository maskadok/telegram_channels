import { ReactNode } from "react";

import { MiniAppInit } from "@/components/mini-app-init";


export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <MiniAppInit />
      <main className="app-container">{children}</main>
    </div>
  );
}
