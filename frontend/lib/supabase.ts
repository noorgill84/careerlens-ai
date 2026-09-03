"use client";

import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";

// Cookie-based client (not plain supabase-js/localStorage) so the session
// is readable both here and in the server-side route handler at
// app/auth/callback/route.ts, and can later be read in Next.js middleware
// for server-side route protection if you extend RequireAuth that way.
export const supabase = createClientComponentClient();

export async function getAccessToken(): Promise<string | null> {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}
