"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Filter, GitCompare } from "lucide-react";
import { formatCurrency, formatDate } from "@/lib/utils";

// Mock data
const archivedProjects = [
  {
    id: "1",
    title: "Lakeside Villas Phase 1",
    status: "COMPLETED",
    completedDate: "2023-12-15",
    budget: 3200000,
    actualCost: 3050000,
    homeAreaSqFt: 3200,
    lotCount: 24,
  },
  {
    id: "2",
    title: "Mountain View Estates",
    status: "COMPLETED",
    completedDate: "2023-08-30",
    budget: 2800000,
    actualCost: 2950000,
    homeAreaSqFt: 2900,
    lotCount: 18,
  },
];

export default function ArchivePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Build Archive</h1>
          <p className="text-gray-600 mt-1">Search and compare completed projects</p>
        </div>
        
        <Button variant="outline">
          <GitCompare className="mr-2 h-4 w-4" />
          Compare Projects
        </Button>
      </div>

      {/* Search & Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search archived projects..."
                  className="w-full pl-10"
                />
              </div>
            </div>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              Advanced Filters
            </Button>
          </div>

          {/* Filter Tags */}
          <div className="flex gap-2 mt-4">
            <div className="text-sm text-gray-600">Quick Filters:</div>
            {["Last 6 Months", "Under Budget", "Over Budget", "Similar Area"].map(
              (filter) => (
                <Button key={filter} variant="outline" size="sm">
                  {filter}
                </Button>
              )
            )}
          </div>
        </CardContent>
      </Card>

      {/* Archived Projects List */}
      <div className="grid gap-4">
        {archivedProjects.map((project) => (
          <Card key={project.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold">{project.title}</h3>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {project.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Completed: {formatDate(project.completedDate)}
                  </p>

                  <div className="grid grid-cols-5 gap-6 mt-4">
                    <div>
                      <div className="text-xs text-gray-500">Budget</div>
                      <div className="font-medium">{formatCurrency(project.budget)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Actual Cost</div>
                      <div className="font-medium">{formatCurrency(project.actualCost)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Variance</div>
                      <div
                        className={`font-medium ${
                          project.actualCost <= project.budget
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {formatCurrency(project.budget - project.actualCost)}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Home Area</div>
                      <div className="font-medium">{project.homeAreaSqFt.toLocaleString()} SF</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Lots</div>
                      <div className="font-medium">{project.lotCount}</div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                  <Button variant="outline" size="sm">
                    Use as Template
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
