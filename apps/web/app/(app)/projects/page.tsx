"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {Plus, Search, Filter } from "lucide-react";
import Link from "next/link";
import { formatCurrency, formatDate } from "@/lib/utils";

// Mock data
const projects = [
  {
    id: "1",
    title: "Sunset Hills Phase 2",
    address: "123 Main St, Austin, TX",
    status: "ACTIVE",
    budget: 2500000,
    homeAreaSqFt: 2800,
    baselineStartDate: "2024-01-15",
    baselineEndDate: "2024-12-31",
  },
  {
    id: "2",
    title: "Downtown Lofts",
    address: "456 Oak Ave, Austin, TX",
    status: "PLANNING",
    budget: 1800000,
    homeAreaSqFt: 2200,
    baselineStartDate: "2024-03-01",
    baselineEndDate: "2025-01-31",
  },
];

export default function ProjectsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-gray-600 mt-1">Manage all your construction projects</p>
        </div>
        
        <Button asChild>
          <Link href="/projects/new">
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search projects..."
                  className="w-full pl-10"
                />
              </div>
            </div>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Projects List */}
      <div className="grid gap-4">
        {projects.map((project) => (
          <Card key={project.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <Link href={`/projects/${project.id}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold">{project.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{project.address}</p>
                    
                    <div className="flex gap-6 mt-4">
                      <div>
                        <div className="text-xs text-gray-500">Budget</div>
                        <div className="font-medium">{formatCurrency(project.budget)}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Area</div>
                        <div className="font-medium">{project.homeAreaSqFt.toLocaleString()} SF</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Start Date</div>
                        <div className="font-medium">{formatDate(project.baselineStartDate)}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">End Date</div>
                        <div className="font-medium">{formatDate(project.baselineEndDate)}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      project.status === "ACTIVE"
                        ? "bg-green-100 text-green-800"
                        : "bg-blue-100 text-blue-800"
                    }`}>
                      {project.status}
                    </span>
                  </div>
                </div>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
