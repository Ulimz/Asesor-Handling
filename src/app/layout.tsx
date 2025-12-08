import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
// import MainNavbar from "@/components/MainNavbar"; // Assuming this component exists or needs creation

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Asistente Azul Handling",
  description: "Resuelve tus dudas sobre el convenio y estatuto.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="dark">
      <body className="min-h-screen font-sans bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
        {/* <MainNavbar /> */}
        <main className="relative min-h-screen flex flex-col">
          {/* Ambient Background */}
          <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-slate-950 to-slate-950 pointer-events-none"></div>
          {/* Glass Orb Effect */}
          <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-indigo-600/10 rounded-[100%] blur-[120px] -z-10 pointer-events-none mix-blend-screen"></div>

          <div className="max-w-7xl mx-auto w-full px-6 py-8 flex-1">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
