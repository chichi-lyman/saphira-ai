/*
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
 */

import Head from 'next/head';

export default function SEOHead() {
  const schemaData = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Saphira AI",
    "operatingSystem": "iOS, Android, Web",
    "applicationCategory": "ProductivityApplication",
    "author": {
      "@type": "Person",
      "name": "Chelsea Megan Woods"
    },
    "copyrightHolder": {
      "@type": "Person",
      "name": "Chelsea Megan Woods"
    },
    "offers": {
      "@type": "AggregateOffer",
      "priceCurrency": "USD",
      "lowPrice": "0.00",
      "highPrice": "49.00",
      "offerCount": "3"
    }
  };

  return (
    <Head>
      {/* Search Engine Optimization */}
      <title>Saphira AI | Speak Upfront. Automate in Silence | By Chelsea Megan Woods</title>
      <meta name="description" content="Saphira AI is your warm conversational companion upfront and silent task executor behind the scenes. Created by Chelsea Megan Woods." />
      <meta name="keywords" content="Saphira AI, Chelsea Megan Woods, AI assistant, automated tasks, voice companion, smart home AI, background task automation" />
      <meta name="author" content="Chelsea Megan Woods" />
      <meta name="copyright" content="Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved." />

      {/* OpenGraph / Facebook Meta Tags */}
      <meta property="og:type" content="website" />
      <meta property="og:title" content="Saphira AI — Created by Chelsea Megan Woods" />
      <meta property="og:description" content="Talk naturally with Saphira while she manages your code, hardware, and schedule in the background." />
      <meta property="og:site_name" content="Woods AI Studio" />

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Saphira AI | By Chelsea Megan Woods" />
      <meta name="twitter:description" content="Speak upfront. Automate in silence." />

      {/* App Store Optimization (ASO) Tags */}
      <meta name="apple-itunes-app" content="app-id=SAPHIRA_APP_ID" />
      <meta name="google-play-app" content="app-id=com.chelseawoodsaistudio.saphira" />

      {/* Structured JSON-LD Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
      />
    </Head>
  );
}
