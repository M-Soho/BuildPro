"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Search, FolderKanban, DollarSign, AlertTriangle, Package } from "lucide-react";
import Link from "next/link";
import { formatCurrency } from "@/lib/utils";

// Mock data - will be replaced with API calls
const kpiData = {
  activeProjects: 12,
  avgCostPerSqFt: 145.50,
  scheduleAlerts: 3,
  materialsTracked: 1247,
};

const recentProjects = [
  {
    id: "1",
    title: "Sunset Hills Phase 2",
    status: "ACTIVE",
    budget: 2500000,
    completion: 65,
  },
  {
    id: "2",
    title: "Downtown Lofts",
    status: "PLANNING",
    budget: 1800000,
    completion: 15,
  },
  {
    id: "3",
    title: "Riverside Commons",
    status: "ACTIVE",
    budget: 3200000,
    completion: 82,
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back! Here's an overview of your projects.
          </p>
        </div>
        
        <div className="flex gap-3">
          <Button variant="outline" asChild>
            <Link href="/archive">
              <Search className="mr-2 h-4 w-4" />
              Search Archive
            </Link>
          </Button>
          <Button asChild>
            <Link href="/projects/new">
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Link>
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Projects
            </CardTitle>
            <FolderKanban className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpiData.activeProjects}</div>
            <p className="text-xs text-muted-foreground">
              Currently in progress
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Avg Cost/SqFt
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(kpiData.avgCostPerSqFt)}
            </div>
            <p className="text-xs text-muted-foreground">
              Across all projects
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Schedule Alerts
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {kpiData.scheduleAlerts}
            </div>
            <p className="text-xs text-muted-foreground">
              Items behind schedule
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Materials Tracked
            </CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {kpiData.materialsTracked.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Line items across projects
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Projects */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Projects</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentProjects.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className="flex items-center justify-between p-4 rounded-lg border hover:bg-gray-50 transition-colors"
              >
                <div className="flex-1">
                  <h3 className="font-semibold">{project.title}</h3>
                  <p className="text-sm text-gray-600">
                    Budget: {formatCurrency(project.budget)} • {project.status}
                  </p>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      {project.completion}% Complete
                    </div>
                    <div className="w-32 h-2 bg-gray-200 rounded-full mt-1">
                      <div
                        className="h-full bg-blue-600 rounded-full"
                        style={{ width: `${project.completion}%` }}
                      />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
          
          <div className="mt-4 text-center">
            <Button variant="outline" asChild>
              <Link href="/projects">View All Projects</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
