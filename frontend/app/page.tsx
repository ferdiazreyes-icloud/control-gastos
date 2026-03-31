"use client";

import { useCallback, useEffect, useState } from "react";
import MovementCard from "@/components/MovementCard";
import EditMovementModal from "@/components/EditMovementModal";
import {
  getMovements,
  updateMovement,
  getCategories,
  getTags,
  processEmails,
  getAuthStatus,
} from "@/lib/api";
import { Category, Movement, Tag } from "@/lib/types";

export default function ReviewPage() {
  const [movements, setMovements] = useState<Movement[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [editingMovement, setEditingMovement] = useState<Movement | null>(null);
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [processResult, setProcessResult] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [movs, cats, tgs, auth] = await Promise.all([
        getMovements({ status: "pending" }),
        getCategories(),
        getTags(),
        getAuthStatus(),
      ]);
      setMovements(movs);
      setCategories(cats);
      setTags(tgs);
      setAuthenticated(auth.authenticated);
    } catch (err) {
      console.error("Error loading data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleProcess = async () => {
    setProcessing(true);
    setProcessResult(null);
    try {
      const result = await processEmails(20);
      setProcessResult(
        `${result.emails_fetched} correos analizados, ${result.movements_stored} movimientos detectados`
      );
      await loadData();
    } catch (err) {
      setProcessResult("Error al procesar correos");
    } finally {
      setProcessing(false);
    }
  };

  const handleConfirm = async (id: string) => {
    await updateMovement(id, { status: "confirmed" });
    setMovements((prev) => prev.filter((m) => m.id !== id));
  };

  const handleDiscard = async (id: string) => {
    await updateMovement(id, { status: "discarded" });
    setMovements((prev) => prev.filter((m) => m.id !== id));
  };

  const handleEdit = (movement: Movement) => {
    setEditingMovement(movement);
  };

  const handleSaveEdit = async (data: Record<string, unknown>) => {
    if (!editingMovement) return;
    await updateMovement(editingMovement.id, data);
    setEditingMovement(null);
    await loadData();
  };

  if (loading) {
    return (
      <div className="text-center py-12 text-slate-500">Cargando...</div>
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Revisar</h1>
          <p className="text-sm text-slate-500">
            {movements.length} movimiento{movements.length !== 1 ? "s" : ""}{" "}
            pendiente{movements.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={handleProcess}
          disabled={processing || !authenticated}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            processing || !authenticated
              ? "bg-slate-200 text-slate-400"
              : "bg-blue-600 text-white active:bg-blue-700"
          }`}
        >
          {processing ? "Procesando..." : "Buscar correos"}
        </button>
      </header>

      {!authenticated && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
          Gmail no conectado.{" "}
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/login`}
            className="underline font-medium"
          >
            Conectar Gmail
          </a>
        </div>
      )}

      {processResult && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 text-sm text-blue-800">
          {processResult}
        </div>
      )}

      {movements.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center">
          <p className="text-slate-600">
            No hay movimientos pendientes por revisar.
          </p>
          <p className="text-slate-400 text-sm mt-2">
            Presiona &quot;Buscar correos&quot; para analizar tus emails.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {movements.map((movement) => (
            <MovementCard
              key={movement.id}
              movement={movement}
              onConfirm={() => handleConfirm(movement.id)}
              onDiscard={() => handleDiscard(movement.id)}
              onEdit={() => handleEdit(movement)}
            />
          ))}
        </div>
      )}

      {editingMovement && (
        <EditMovementModal
          movement={editingMovement}
          categories={categories}
          tags={tags}
          onSave={handleSaveEdit}
          onClose={() => setEditingMovement(null)}
        />
      )}
    </div>
  );
}
