"use client";

import { useEffect, useState, useCallback } from "react";
import MovementCard from "@/components/MovementCard";
import EditMovementModal from "@/components/EditMovementModal";
import ConfirmDialog from "@/components/ConfirmDialog";
import { getMovements, getCategories, getTags, updateMovement } from "@/lib/api";
import { Movement, MovementStatus, Category, Tag } from "@/lib/types";

interface StatusChange {
  movementId: string;
  newStatus: MovementStatus;
  merchantOrConcept: string;
}

export default function HistoryPage() {
  const [movements, setMovements] = useState<Movement[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<MovementStatus | "all">("confirmed");
  const [editingMovement, setEditingMovement] = useState<Movement | null>(null);
  const [statusChange, setStatusChange] = useState<StatusChange | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const params = filter === "all" ? {} : { status: filter as MovementStatus };
      const [data, cats, tgs] = await Promise.all([
        getMovements(params),
        getCategories(),
        getTags(),
      ]);
      setMovements(data);
      setCategories(cats);
      setTags(tgs);
    } catch (err) {
      console.error("Error loading history:", err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleStatusChange = async () => {
    if (!statusChange) return;
    try {
      await updateMovement(statusChange.movementId, { status: statusChange.newStatus });
      setStatusChange(null);
      await loadData();
    } catch (err) {
      console.error("Error changing status:", err);
    }
  };

  const handleSaveEdit = async (data: Record<string, unknown>) => {
    if (!editingMovement) return;
    try {
      await updateMovement(editingMovement.id, data);
      setEditingMovement(null);
      await loadData();
    } catch (err) {
      console.error("Error saving edit:", err);
    }
  };

  const totalAmount = movements
    .filter((m) => m.type === "expense")
    .reduce((sum, m) => sum + Number(m.amount), 0);

  const statusLabel = (s: MovementStatus) =>
    s === "confirmed" ? "confirmar" : "descartar";

  return (
    <div className="space-y-4">
      <header>
        <h1 className="text-xl font-bold text-slate-800">Historial</h1>
        <p className="text-sm text-slate-500">
          {movements.length} movimiento{movements.length !== 1 ? "s" : ""}
          {filter === "confirmed" && totalAmount > 0 && (
            <span className="ml-2 text-red-600 font-medium">
              Total gastos: ${totalAmount.toLocaleString("es-MX", { minimumFractionDigits: 2 })}
            </span>
          )}
        </p>
      </header>

      <div className="flex gap-2">
        {(["confirmed", "discarded", "all"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-sm ${
              filter === f
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-600 border"
            }`}
          >
            {f === "confirmed"
              ? "Confirmados"
              : f === "discarded"
                ? "Descartados"
                : "Todos"}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-8 text-slate-500">Cargando...</div>
      ) : movements.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center">
          <p className="text-slate-500">No hay movimientos en esta vista.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {movements.map((movement) => (
            <MovementCard
              key={movement.id}
              movement={movement}
              showActions={true}
              onEdit={() => setEditingMovement(movement)}
              onConfirm={() =>
                setStatusChange({
                  movementId: movement.id,
                  newStatus: "confirmed",
                  merchantOrConcept:
                    movement.merchant || movement.concept || "este movimiento",
                })
              }
              onDiscard={() =>
                setStatusChange({
                  movementId: movement.id,
                  newStatus: "discarded",
                  merchantOrConcept:
                    movement.merchant || movement.concept || "este movimiento",
                })
              }
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

      {statusChange && (
        <ConfirmDialog
          title={`¿${statusChange.newStatus === "confirmed" ? "Confirmar" : "Descartar"} movimiento?`}
          message={`¿Seguro que quieres ${statusLabel(statusChange.newStatus)} "${statusChange.merchantOrConcept}"?`}
          confirmLabel={statusChange.newStatus === "confirmed" ? "Confirmar" : "Descartar"}
          onConfirm={handleStatusChange}
          onCancel={() => setStatusChange(null)}
        />
      )}
    </div>
  );
}
