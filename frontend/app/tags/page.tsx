"use client";

import { useEffect, useState } from "react";
import { getTags, createTag, deleteTag } from "@/lib/api";
import { Tag } from "@/lib/types";

export default function TagsPage() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [color, setColor] = useState("#3b82f6");

  const load = async () => {
    try {
      const data = await getTags();
      setTags(data);
    } catch (err) {
      console.error("Error loading tags:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    await createTag({ name: name.trim(), color: color || undefined });
    setName("");
    setShowForm(false);
    await load();
  };

  const handleDelete = async (id: string) => {
    await deleteTag(id);
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
        <h1 className="text-xl font-bold text-slate-800">Tags</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium active:bg-blue-700"
        >
          {showForm ? "Cancelar" : "+ Nuevo"}
        </button>
      </header>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nombre del tag"
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
          <div className="flex gap-3 items-center">
            <label className="text-sm text-slate-600">Color:</label>
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
            Crear tag
          </button>
        </div>
      )}

      {tags.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center">
          <p className="text-slate-500">No hay tags creados.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {tags.map((tag) => (
            <div
              key={tag.id}
              className="bg-white rounded-xl shadow-sm p-4 flex justify-between items-center"
            >
              <div className="flex items-center gap-3">
                <span
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: tag.color || "#94a3b8" }}
                />
                <span className="font-medium">{tag.name}</span>
              </div>
              <button
                onClick={() => handleDelete(tag.id)}
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
