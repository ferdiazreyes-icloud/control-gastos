"use client";

import { useEffect, useState } from "react";
import { getSenders, createSender, deleteSender } from "@/lib/api";
import { Sender } from "@/lib/types";

export default function SendersPage() {
  const [senders, setSenders] = useState<Sender[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [emailPattern, setEmailPattern] = useState("");
  const [name, setName] = useState("");

  const load = async () => {
    try {
      const data = await getSenders();
      setSenders(data);
    } catch (err) {
      console.error("Error loading senders:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (!emailPattern.trim() || !name.trim()) return;
    await createSender({
      email_pattern: emailPattern.trim(),
      name: name.trim(),
    });
    setEmailPattern("");
    setName("");
    setShowForm(false);
    await load();
  };

  const handleDelete = async (id: string) => {
    await deleteSender(id);
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
        <div>
          <h1 className="text-xl font-bold text-slate-800">Remitentes</h1>
          <p className="text-sm text-slate-500">
            Solo se analizan correos de estos remitentes
          </p>
        </div>
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
            placeholder="Nombre (ej: Banorte)"
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
          <input
            value={emailPattern}
            onChange={(e) => setEmailPattern(e.target.value)}
            placeholder="Patron de email (ej: @banorte.com)"
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
          <p className="text-xs text-slate-400">
            Usa @ para dominios completos (ej: @banco.com) o email completo
            (ej: alertas@banco.com)
          </p>
          <button
            onClick={handleCreate}
            className="w-full bg-green-500 text-white py-2 rounded-lg text-sm font-medium active:bg-green-600"
          >
            Agregar remitente
          </button>
        </div>
      )}

      {senders.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center">
          <p className="text-slate-500">No hay remitentes configurados.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {senders.map((sender) => (
            <div
              key={sender.id}
              className="bg-white rounded-xl shadow-sm p-4 flex justify-between items-center"
            >
              <div>
                <p className="font-medium text-slate-800">{sender.name}</p>
                <p className="text-sm text-slate-500">
                  {sender.email_pattern}
                </p>
              </div>
              <button
                onClick={() => handleDelete(sender.id)}
                className="text-red-400 text-sm active:text-red-600"
              >
                Quitar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
