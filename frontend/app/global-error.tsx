"use client";

import { Button } from "@/components/ui/Button";

export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html>
      <body className="flex min-h-screen flex-col items-center justify-center bg-base text-text-primary">
        <p className="mb-2 font-display text-xl">Something went wrong</p>
        <p className="mb-6 text-sm text-text-muted">Please try again — if the problem continues, reload the page.</p>
        <Button onClick={reset}>Try again</Button>
      </body>
    </html>
  );
}
