import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AIVisibilityBot | AI Visibility Audit for SEO, AEO & GEO",
  description:
    "Free AI visibility audit engine. Run 51+ checks across SEO, AEO, and GEO to discover how ChatGPT, Perplexity, and Gemini see your brand.",
  keywords: [
    "AEO", "GEO", "SEO", "AI visibility audit", "answer engine optimization",
    "generative engine optimization", "AI citation", "ChatGPT SEO",
  ],
  robots: { index: true, follow: true },
  openGraph: {
    title: "AIVisibilityBot | AI Visibility Audit for SEO, AEO & GEO",
    description: "Run 51+ automated checks. See how AI engines understand your site.",
    type: "website",
    siteName: "AIVisibilityBot",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "AIVisibilityBot | AI Visibility Audit",
    description: "Free AI visibility audit. 51+ checks across SEO, AEO, and GEO.",
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  name: "AIVisibilityBot",
  description: "The world's first autonomous AEO + GEO + SEO audit platform.",
  applicationCategory: "SEO Tool",
  operatingSystem: "Web",
  offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
