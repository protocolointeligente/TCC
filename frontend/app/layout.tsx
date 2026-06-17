import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Academia IA",
  description: "Ferramenta para TCC, revisão bibliográfica e pesquisa científica",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
