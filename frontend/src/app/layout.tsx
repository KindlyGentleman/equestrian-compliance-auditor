import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Maison Équestre Atelier Pro | Equestrian Compliance & Specification Auditor",
  description:
    "FEI Olympic Regulations & Technical Specification Compliance Auditor for Luxury Equestrian Wear",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-luxury-parchment text-luxury-slate font-sans antialiased selection:bg-equestrian-mist selection:text-equestrian-forest">
        {children}
      </body>
    </html>
  );
}
