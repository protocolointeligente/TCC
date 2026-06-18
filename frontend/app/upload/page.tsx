"use client";
import { useState } from "react";
import { useUser } from "@clerk/nextjs";
import { buildHeaders } from "@/lib/api";

export default function UploadPage() {
  const { user } = useUser();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function upload() {
    if (!file || !user) return;
    setUploading(true);
    setError(null);
    setPreview("");

    const formData = new FormData();
    formData.append("file", file);

    const headers = buildHeaders(user.id, user.primaryEmailAddress?.emailAddress);
    const { "Content-Type": _, ...headersWithoutContentType } = headers as Record<string, string>;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/upload-pdf`, {
        method: "POST",
        headers: headersWithoutContentType,
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail || "Erro no upload.");
        return;
      }
      setPreview(data.preview);
    } catch {
      setError("Erro de conexão com o servidor.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <main className="min-h-screen p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Upload de PDF</h1>

        <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800">
          <label className="block mb-2 font-medium">Selecionar arquivo PDF</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="mb-4 text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-slate-800 file:text-white hover:file:bg-slate-700"
          />

          <button
            onClick={upload}
            disabled={!file || uploading}
            className="bg-violet-600 hover:bg-violet-700 disabled:bg-slate-700 disabled:cursor-not-allowed px-5 py-2 rounded-xl font-medium text-sm"
          >
            {uploading ? "Enviando..." : "Enviar PDF"}
          </button>
        </div>

        {error && (
          <div className="mt-4 bg-red-900/40 border border-red-700 rounded-xl p-4 text-red-300 text-sm">
            {error}
          </div>
        )}

        {preview && (
          <div className="mt-6 bg-slate-900 rounded-2xl p-6 border border-slate-800">
            <h2 className="font-bold mb-3">Prévia do texto extraído</h2>
            <div className="bg-slate-950 rounded-xl p-4 text-sm text-slate-300 whitespace-pre-wrap leading-6 max-h-96 overflow-auto">
              {preview}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
