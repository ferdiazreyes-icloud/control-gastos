"use client";

import { Category, Movement, Tag } from "@/lib/types";
import MovementCard from "./MovementCard";

interface DuplicateGroupProps {
  movements: Movement[];
  onKeep: (id: string) => void;
  onNotDuplicate: (id: string) => void;
  onEdit: (movement: Movement) => void;
}

export default function DuplicateGroup({
  movements,
  onKeep,
  onNotDuplicate,
  onEdit,
}: DuplicateGroupProps) {
  return (
    <div className="border-2 border-amber-300 bg-amber-50 rounded-xl p-3 space-y-3">
      <div className="flex justify-between items-center">
        <p className="text-sm font-semibold text-amber-800">
          Posible duplicado ({movements.length} movimientos)
        </p>
        <button
          onClick={() => movements.forEach((m) => onNotDuplicate(m.id))}
          className="text-xs text-amber-700 underline"
        >
          No son duplicados
        </button>
      </div>

      {movements.map((movement) => (
        <div key={movement.id} className="space-y-2">
          <MovementCard
            movement={movement}
            showActions={false}
          />
          <div className="flex gap-2 px-1">
            <button
              onClick={() => onKeep(movement.id)}
              className="flex-1 bg-green-500 text-white text-sm font-medium py-2 rounded-lg active:bg-green-600"
            >
              Conservar este
            </button>
            <button
              onClick={() => onEdit(movement)}
              className="bg-slate-200 text-slate-700 text-sm font-medium py-2 px-4 rounded-lg active:bg-slate-300"
            >
              Editar
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
