"use client";

import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";

// Cookie-based client (not plain supabase-js/localStorage) so the session
// is readable both here and in the server-side route handler at
// app/auth/callback/route.ts, and can later be read in Next.js middleware
// for server-side route protection if you extend RequireAuth that way.
//
// IMPORTANT: falls back to a syntactically-valid placeholder URL/key when
// the real env vars aren't set, instead of letting the Supabase client
// constructor throw. Next.js prerenders every page that imports this file
// at BUILD time (even pages that only use Supabase after a user interacts
// with them), so an invalid/missing env var here fails the entire
// `next build` — not just breaks auth at runtime. With the fallback, a
// missing env var instead just means auth silently doesn't work until you
// set the real values and redeploy, which is a much easier failure to debug.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder-anon-key";

if (typeof window !== "undefined" && (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)) {
  console.warn(
    "[CareerLens] NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY are not set. " +
      "Auth will not work until they're configured (Vercel: Settings → Environment Variables)."
  );
}

export const supabase = createClientComponentClient({ supabaseUrl, supabaseKey: supabaseAnonKey });

export async function getAccessToken(): Promise<string | null> {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}
