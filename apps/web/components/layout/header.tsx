"use client";

import { Button } from "@/components/ui/button";
import { Bell, User } from "lucide-react";

export function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          {/* Dynamic page title can go here */}
        </h2>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Tenant Switcher Placeholder */}
        <div className="text-sm text-gray-600">
          <select className="rounded border px-2 py-1">
            <option>Default Tenant</option>
          </select>
        </div>
        
        {/* Notifications */}
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
        </Button>
        
        {/* User Menu */}
        <Button variant="ghost" size="icon">
          <User className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
}
