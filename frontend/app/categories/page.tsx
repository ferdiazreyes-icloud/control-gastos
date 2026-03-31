"use client";

import { useEffect, useState } from "react";
import { getCategories, createCategory, deleteCategory } from "@/lib/api";
import { Category } from "@/lib/types";

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [icon, setIcon] = useState("");
  const [color, setColor] = useState("#3b82f6");

  const load = async () => {
    try {
      const data = await getCategories();
      setCategories(data);
    } catch (err) {
      console.error("Error loading categories:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    await createCategory({
      name: name.trim(),
      icon: icon || undefined,
      color: color || undefined,
    });
    setName("");
    setIcon("");
    setShowForm(false);
    await load();
  };

  const handleDelete = async (id: string) => {
    await deleteCategory(id);
    await load();
  };

  if (loading) {
    return (
      <div className="text-center py-12 text-slate-500">Cargando...</div>
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex justify-between items-center">
        <h1 className="text-xl font-bold text-slate-800">Categorias</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium active:bg-blue-700"
        >
          {showForm ? "Cancelar" : "+ Nueva"}
        </button>
      </header>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nombre de la categoria"
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
          <div className="flex gap-3">
            <input
              value={icon}
              onChange={(e) => setIcon(e.target.value)}
              placeholder="Icono (emoji)"
              className="flex-1 border rounded-lg px-3 py-2 text-sm"
            />
            <input
              type="color"
              value={color}
              onChange={(e) => setColor(e.target.value)}
              className="w-12 h-10 border rounded-lg cursor-pointer"
            />
          </div>
          <button
            onClick={handleCreate}
            className="w-full bg-green-500 text-white py-2 rounded-lg text-sm font-medium active:bg-green-600"
          >
            Crear categoria
          </button>
        </div>
      )}

      {categories.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center">
          <p className="text-slate-500">No hay categorias creadas.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {categories.map((cat) => (
            <div
              key={cat.id}
              className="bg-white rounded-xl shadow-sm p-4 flex justify-between items-center"
            >
              <div className="flex items-center gap-3">
                <span
                  className="w-8 h-8 rounded-full flex items-center justify-center text-sm"
                  style={{ backgroundColor: cat.color ? `${cat.color}20` : "#f1f5f9" }}
                >
                  {cat.icon || "📁"}
                </span>
                <span className="font-medium">{cat.name}</span>
              </div>
              <button
                onClick={() => handleDelete(cat.id)}
                className="text-red-400 text-sm active:text-red-600"
              >
                Eliminar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
