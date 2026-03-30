export default function Home() {
  return (
    <div className="space-y-6">
      <header className="text-center">
        <h1 className="text-2xl font-bold text-slate-800">Control Gastos</h1>
        <p className="text-slate-500 text-sm mt-1">
          AI-powered expense tracker
        </p>
      </header>

      <section className="bg-white rounded-xl shadow-sm p-6 text-center">
        <p className="text-slate-600">
          No hay movimientos pendientes por revisar.
        </p>
        <p className="text-slate-400 text-sm mt-2">
          Los movimientos aparecerán aquí cuando se procesen tus correos.
        </p>
      </section>
    </div>
  );
}
