"use client";

import { useEffect, useState } from "react";
import MovementCard from "@/components/MovementCard";
import { getMovements } from "@/lib/api";
import { Movement, MovementStatus } from "@/lib/types";

export default function HistoryPage() {
  const [movements, setMovements] = useState<Movement[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<MovementStatus | "all">("confirmed");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const params = filter === "all" ? {} : { status: filter as MovementStatus };
        const data = await getMovements(params);
        setMovements(data);
      } catch (err) {
        console.error("Error loading history:", err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [filter]);

  const totalAmount = movements
    .filter((m) => m.type === "expense")
    .reduce((sum, m) => sum + Number(m.amount), 0);

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
              showActions={false}
            />
          ))}
        </div>
      )}
    </div>
  );
}
