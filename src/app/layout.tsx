import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
// import MainNavbar from "@/components/MainNavbar"; // Assuming this component exists or needs creation

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Asistente Handling",
  description: "Resuelve tus dudas sobre el convenio y estatuto.",
  manifest: '/manifest.json',
  icons: {
    icon: '/icon-optimized.png',
    apple: '/icon-optimized.png',
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Asistente',
  },
  verification: {
    google: 'KwLpXvOMw7FoITQi8HUaHAlKZt0JHJVCABoGfPcDuUI',
  },
};

export const viewport: Viewport = {
  themeColor: '#0f172a',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  interactiveWidget: 'resizes-content',
};

import CookieBanner from "@/components/legal/CookieBanner";
import { ThemeProvider } from "@/context/ThemeContext";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="dark">
      <body className="min-h-screen font-sans bg-slate-950 text-slate-100 selection:bg-cyan-500/30 transition-colors duration-300">
        <ThemeProvider>
          {/* Main content wrapper with theme-aware background */}
          <div className="relative min-h-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-primary)] transition-colors duration-300">
            {/* <MainNavbar /> */}
            <main className="relative min-h-screen flex flex-col flex-1">
              {/* Ambient Background - Adjusted for Light/Dark */}
              <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-slate-950 to-slate-950 pointer-events-none opacity-100 dark:opacity-100 light:opacity-0 transition-opacity"></div>

              <div className="max-w-7xl mx-auto w-full px-6 py-8 flex-1">
                {children}
              </div>
            </main>
            <CookieBanner />
            {/* Version Marker for User Verification */}
            <div className="fixed bottom-1 right-1 text-[10px] text-slate-700 pointer-events-none opacity-50 z-50">
              v1.7-FIXED (URL+CORS)
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
