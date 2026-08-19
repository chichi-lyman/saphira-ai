/* Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved. */

import type { NextApiRequest, NextApiResponse } from 'next';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', { apiVersion: '2024-06-20' });
const BASE_URL = (process.env.NEXT_PUBLIC_BASE_URL || process.env.PRODUCTION_DOMAIN_URL || 'http://localhost:3000').replace(/\/$/, '');

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  if (!process.env.STRIPE_SECRET_KEY) return res.status(503).json({ error: 'Stripe is not configured' });

  try {
    const priceId = process.env.STRIPE_PRICE_MONTHLY;
    const session = priceId
      ? await stripe.checkout.sessions.create({
          mode: 'subscription',
          line_items: [{ price: priceId, quantity: 1 }],
          success_url: `${BASE_URL}/success.html?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${BASE_URL}/?canceled=1`,
          metadata: { plan: 'saphira-monthly', creator: 'Chelsea Megan Woods' },
        })
      : await stripe.checkout.sessions.create({
          mode: 'subscription',
          line_items: [{
            price_data: {
              currency: 'usd',
              unit_amount: 19900,
              recurring: { interval: 'month' },
              product_data: {
                name: 'Saphira AI — Client Acquisition',
                description: 'Conversational lead generation and governed sales operations.',
              },
            },
            quantity: 1,
          }],
          success_url: `${BASE_URL}/success.html?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${BASE_URL}/?canceled=1`,
          metadata: { plan: 'saphira-monthly', creator: 'Chelsea Megan Woods' },
        });

    return res.status(200).json({ url: session.url });
  } catch (err) {
    console.error('Stripe checkout error', err);
    return res.status(502).json({ error: 'Stripe checkout could not be created' });
  }
}
