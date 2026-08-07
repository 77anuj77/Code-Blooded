"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { getPatientHistoryRemote } from "@/lib/api";
import { useApiActor } from "@/lib/use-api-actor";
import type { PatientHistoryResponse } from "@/types/lumina";

export function PatientHistoryPanel({ patientId }: { patientId: string }) {
  const t = useTranslations("patientHistory");
  const actor = useApiActor();
  const [history, setHistory] = useState<PatientHistoryResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "pending" | "ready" | "error">("loading");

  useEffect(() => {
    if (!actor || actor.role !== "doctor" || !patientId) return;
    getPatientHistoryRemote(patientId, actor)
      .then((data) => {
        setHistory(data);
        setStatus("ready");
      })
      .catch((err: Error) => {
        setStatus(err.message.includes("403") || err.message.toLowerCase().includes("not approved") ? "pending" : "error");
      });
  }, [actor, patientId]);

  if (!actor || actor.role !== "doctor" || !patientId) return null;

  return (
    <div className="rounded border border-[#DDE3ED] bg-white p-5">
      <p className="text-[14px] font-normal text-[#0D1B2A]">{t("title")}</p>
      {status === "loading" && <p className="mt-2 text-[13px] text-[#8A94A6]">…</p>}
      {status === "pending" && <p className="mt-2 text-[13px] text-[#D4860A]">{t("pending")}</p>}
      {status === "error" && <p className="mt-2 text-[13px] text-[#B42318]">{t("loadFailed")}</p>}
      {status === "ready" && history && (
        <div className="mt-3">
          <p className="text-[13.5px] text-[#0D1B2A]">{history.summary}</p>
          {history.timeline.length > 0 && (
            <div className="mt-4">
              <p className="text-[11px] font-normal uppercase tracking-[0.08em] text-[#8A94A6]">{t("timelineTitle")}</p>
              <div className="mt-2 space-y-1.5">
                {history.timeline.map((entry) => (
                  <div key={entry.caseId} className="flex items-center justify-between text-[12.5px] text-[#4A5568]">
                    <span>{entry.topDiagnosis}</span>
                    <span className="text-[#8A94A6]">{new Date(entry.date).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {history.timeline.length === 0 && <p className="mt-2 text-[13px] text-[#8A94A6]">{t("empty")}</p>}
        </div>
      )}
    </div>
  );
}
