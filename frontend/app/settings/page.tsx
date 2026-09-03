"use client";

import { useState } from "react";
import { DashboardCard } from "@/components/ui/DashboardCard";
import { Button } from "@/components/ui/Button";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError } from "@/lib/api";
import { Trash2, LogOut } from "lucide-react";

export default function SettingsPage() {
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deleted, setDeleted] = useState<number | null>(null);
  const { user } = useAuth();

  async function handleDeleteAllData() {
    setDeleting(true);
    setDeleteError(null);
    try {
      const res = await api.deleteAllData();
      setDeleted(res.deleted_count);
      setConfirmingDelete(false);
    } catch (e) {
      setDeleteError(e instanceof ApiError ? e.message : "Couldn't delete your data. Please try again.");
    } finally {
      setDeleting(false);
    }
  }

  async function handleSignOut() {
    await supabase.auth.signOut();
    window.location.href = "/";
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="mb-2">
        <h1 className="font-display text-2xl font-medium">Settings</h1>
        <p className="text-sm text-text-muted">Manage your account and data.</p>
      </div>

      <DashboardCard title="Account">
        {user?.email && <p className="mb-4 text-sm text-text-muted">Signed in as {user.email}</p>}
        <Button variant="secondary" onClick={handleSignOut}>
          <LogOut size={15} /> Sign out
        </Button>
      </DashboardCard>

      <DashboardCard title="Your data">
        <p className="mb-4 text-sm text-text-muted">
          Deleting your data permanently removes your uploaded resumes, analyses, and history.
          This cannot be undone.
        </p>
        {deleted !== null && (
          <p className="mb-3 text-sm text-signal-good">Deleted {deleted} resume(s) and their analyses.</p>
        )}
        {deleteError && <p className="mb-3 text-sm text-signal-bad">{deleteError}</p>}
        {!confirmingDelete ? (
          <Button variant="secondary" onClick={() => setConfirmingDelete(true)}>
            <Trash2 size={15} /> Delete all my data
          </Button>
        ) : (
          <div className="flex items-center gap-3">
            <p className="text-sm text-signal-bad">Are you sure? This is permanent.</p>
            <Button
              variant="secondary"
              className="border-signal-bad/40 text-signal-bad"
              onClick={handleDeleteAllData}
              disabled={deleting}
            >
              {deleting ? "Deleting…" : "Confirm delete"}
            </Button>
            <Button variant="ghost" onClick={() => setConfirmingDelete(false)} disabled={deleting}>Cancel</Button>
          </div>
        )}
      </DashboardCard>
    </div>
  );
}
