/*
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
 */

import type { NextApiRequest, NextApiResponse } from 'next';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
  apiVersion: '2024-06-20',
});

const PRICE_IDS: Record<string, string | undefined> = {
  free: undefined, // handled as free signup
  monthly: process.env.STRIPE_PRICE_MONTHLY,
  pro: process.env.STRIPE_PRICE_PRO,
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { tier } = req.body;

  if (tier === 'free') {
    return res.status(200).json({ url: '/dashboard?tier=free' });
  }

  const priceId = PRICE_IDS[tier];
  if (!priceId) {
    return res.status(400).json({ error: 'Invalid tier or missing Stripe price ID' });
  }

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${process.env.NEXT_PUBLIC_BASE_URL}/dashboard?success=1`,
      cancel_url: `${process.env.NEXT_PUBLIC_BASE_URL}/?canceled=1`,
      metadata: { tier, creator: 'Chelsea Megan Woods' },
    });

    return res.status(200).json({ url: session.url });
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
}
