"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Revisar", icon: "📋" },
  { href: "/history", label: "Historial", icon: "📊" },
  { href: "/categories", label: "Categorías", icon: "🏷️" },
  { href: "/tags", label: "Tags", icon: "🔖" },
  { href: "/senders", label: "Remitentes", icon: "📨" },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 px-2 py-1 z-50">
      <div className="max-w-md mx-auto flex justify-around">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center py-2 px-3 text-xs ${
                isActive
                  ? "text-blue-600 font-semibold"
                  : "text-slate-500"
              }`}
            >
              <span className="text-lg mb-0.5">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
