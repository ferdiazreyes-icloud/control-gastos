"use client";

import { useEffect, useState } from "react";
import { Category, Movement, Tag } from "@/lib/types";

interface EditMovementModalProps {
  movement: Movement;
  categories: Category[];
  tags: Tag[];
  onSave: (data: {
    concept?: string;
    merchant?: string;
    amount?: string;
    category_id?: string | null;
    tag_ids?: string[];
    type?: string;
  }) => void;
  onClose: () => void;
}

export default function EditMovementModal({
  movement,
  categories,
  tags,
  onSave,
  onClose,
}: EditMovementModalProps) {
  const [concept, setConcept] = useState(movement.concept || "");
  const [merchant, setMerchant] = useState(movement.merchant || "");
  const [amount, setAmount] = useState(movement.amount);
  const [type, setType] = useState(movement.type);
  const [categoryId, setCategoryId] = useState(
    movement.category?.id || ""
  );
  const [selectedTags, setSelectedTags] = useState<string[]>(
    movement.tags.map((t) => t.id)
  );

  const toggleTag = (tagId: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagId)
        ? prev.filter((id) => id !== tagId)
        : [...prev, tagId]
    );
  };

  const handleSave = () => {
    onSave({
      concept: concept || undefined,
      merchant: merchant || undefined,
      amount,
      type,
      category_id: categoryId || null,
      tag_ids: selectedTags,
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end">
      <div className="bg-white w-full max-h-[85vh] rounded-t-2xl overflow-y-auto">
        <div className="sticky top-0 bg-white p-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-bold">Editar movimiento</h2>
          <button onClick={onClose} className="text-slate-400 text-2xl">
            &times;
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Comercio
            </label>
            <input
              value={merchant}
              onChange={(e) => setMerchant(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
              placeholder="Nombre del comercio"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Concepto
            </label>
            <input
              value={concept}
              onChange={(e) => setConcept(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
              placeholder="Descripcion del gasto"
            />
          </div>

          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Monto
              </label>
              <input
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                type="number"
                step="0.01"
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div className="w-28">
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Tipo
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as typeof type)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              >
                <option value="expense">Gasto</option>
                <option value="income">Ingreso</option>
                <option value="transfer">Transferencia</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Categoria
            </label>
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              <option value="">Sin categoria</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.icon} {cat.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Tags
            </label>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <button
                  key={tag.id}
                  onClick={() => toggleTag(tag.id)}
                  className={`px-3 py-1 rounded-full text-sm border ${
                    selectedTags.includes(tag.id)
                      ? "bg-blue-100 border-blue-400 text-blue-700"
                      : "bg-white border-slate-300 text-slate-600"
                  }`}
                >
                  {tag.name}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleSave}
            className="w-full bg-blue-600 text-white font-medium py-3 rounded-lg active:bg-blue-700"
          >
            Guardar cambios
          </button>
        </div>
      </div>
    </div>
  );
}
