import { ClerkProvider, SignedIn, SignedOut, UserButton, SignInButton } from "@clerk/nextjs";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Academia IA",
  description: "Ferramenta para TCC, revisão bibliográfica e pesquisa científica",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="pt-BR">
        <body className="bg-slate-950 text-white">
          <header className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
            <a href="/" className="font-bold text-lg tracking-tight">
              Academia IA
            </a>
            <nav className="flex items-center gap-4 text-sm">
              <SignedIn>
                <a href="/history" className="text-slate-300 hover:text-white">Histórico</a>
                <a href="/cep" className="text-slate-300 hover:text-white">CEP</a>
                <a href="/upload" className="text-slate-300 hover:text-white">PDF</a>
                <a href="/pricing" className="text-slate-300 hover:text-white">Planos</a>
                <UserButton />
              </SignedIn>
              <SignedOut>
                <a href="/pricing" className="text-slate-300 hover:text-white">Planos</a>
                <SignInButton />
              </SignedOut>
            </nav>
          </header>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
