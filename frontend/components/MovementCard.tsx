"use client";

import { Movement } from "@/lib/types";

const typeLabels = {
  income: { label: "Ingreso", color: "text-green-600", sign: "+" },
  expense: { label: "Gasto", color: "text-red-600", sign: "-" },
  transfer: { label: "Transferencia", color: "text-blue-600", sign: "" },
};

interface MovementCardProps {
  movement: Movement;
  onConfirm?: () => void;
  onDiscard?: () => void;
  onEdit?: () => void;
  showActions?: boolean;
  showEmailInfo?: boolean;
}

export default function MovementCard({
  movement,
  onConfirm,
  onDiscard,
  onEdit,
  showActions = true,
  showEmailInfo = false,
}: MovementCardProps) {
  const typeInfo = typeLabels[movement.type];
  const date = new Date(movement.movement_date);
  const formattedDate = date.toLocaleDateString("es-MX", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
      <div className="flex justify-between items-start">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-slate-800 truncate">
            {movement.merchant || movement.concept || "Sin concepto"}
          </p>
          <p className="text-sm text-slate-500 truncate">
            {movement.concept && movement.merchant ? movement.concept : ""}
          </p>
        </div>
        <p className={`font-bold text-lg ${typeInfo.color} shrink-0 ml-3`}>
          {typeInfo.sign}${Number(movement.amount).toLocaleString("es-MX", {
            minimumFractionDigits: 2,
          })}{" "}
          <span className="text-xs font-normal">{movement.currency}</span>
        </p>
      </div>

      <div className="flex flex-wrap gap-2 text-xs text-slate-500">
        <span>{formattedDate}</span>
        {movement.account && (
          <span className="bg-slate-100 px-2 py-0.5 rounded">
            {movement.account}
          </span>
        )}
        {movement.category && (
          <span
            className="px-2 py-0.5 rounded"
            style={{
              backgroundColor: movement.category.color
                ? `${movement.category.color}20`
                : "#f1f5f9",
              color: movement.category.color || "#64748b",
            }}
          >
            {movement.category.icon} {movement.category.name}
          </span>
        )}
        {movement.tags.map((tag) => (
          <span
            key={tag.id}
            className="px-2 py-0.5 rounded"
            style={{
              backgroundColor: tag.color ? `${tag.color}20` : "#f1f5f9",
              color: tag.color || "#64748b",
            }}
          >
            {tag.name}
          </span>
        ))}
      </div>

      {showEmailInfo && movement.source_email_id && (
        <div className="bg-slate-50 rounded-lg p-2.5 space-y-1 text-xs">
          {movement.source_email_sender && (
            <p className="text-slate-600">
              <span className="font-medium">De:</span>{" "}
              {movement.source_email_sender}
            </p>
          )}
          {movement.source_email_subject && (
            <p className="text-slate-500 truncate">
              <span className="font-medium">Asunto:</span>{" "}
              {movement.source_email_subject}
            </p>
          )}
          <a
            href={`https://mail.google.com/mail/u/0/#inbox/${movement.source_email_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline"
          >
            Ver correo en Gmail
          </a>
        </div>
      )}

      {showActions && movement.status === "pending" && (
        <div className="flex gap-2 pt-1">
          <button
            onClick={onConfirm}
            className="flex-1 bg-green-500 text-white text-sm font-medium py-2 rounded-lg active:bg-green-600"
          >
            Confirmar
          </button>
          <button
            onClick={onEdit}
            className="flex-1 bg-slate-200 text-slate-700 text-sm font-medium py-2 rounded-lg active:bg-slate-300"
          >
            Editar
          </button>
          <button
            onClick={onDiscard}
            className="flex-1 bg-red-100 text-red-600 text-sm font-medium py-2 rounded-lg active:bg-red-200"
          >
            Descartar
          </button>
        </div>
      )}

      {movement.status === "confirmed" && (
        <div className="text-xs text-green-600 font-medium">Confirmado</div>
      )}
      {movement.status === "discarded" && (
        <div className="text-xs text-red-500 font-medium">Descartado</div>
      )}
    </div>
  );
}
