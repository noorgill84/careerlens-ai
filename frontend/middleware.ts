import { createMiddlewareClient } from "@supabase/auth-helpers-nextjs";
import { NextResponse, type NextRequest } from "next/server";

// Refreshes the Supabase session cookie so it doesn't silently expire
// while the user is active. This does NOT gate routes itself — RequireAuth
// (client-side) handles redirecting unauthenticated users away from
// protected pages; this middleware's only job is keeping the session fresh.
export async function middleware(request: NextRequest) {
  const response = NextResponse.next();
  const supabase = createMiddlewareClient({ req: request, res: response });
  await supabase.auth.getSession();
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
