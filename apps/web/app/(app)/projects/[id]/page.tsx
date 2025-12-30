"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Edit, Trash2 } from "lucide-react";
import Link from "next/link";
import { formatCurrency, formatDate, formatNumber } from "@/lib/utils";

// Mock data
const project = {
  id: "1",
  title: "Sunset Hills Phase 2",
  description: "24-unit residential development with premium finishes",
  address: "123 Main St, Austin, TX 78701",
  status: "ACTIVE",
  budget: 2500000,
  homeAreaSqFt: 2800,
  lotDepth: 120,
  lotWidth: 50,
  baselineStartDate: "2024-01-15",
  baselineEndDate: "2024-12-31",
  actualStartDate: "2024-01-15",
  createdAt: "2023-12-01T10:00:00Z",
};

const lots = [
  { id: "1", lotNumber: "101", status: "ACTIVE", notes: "Premium corner lot" },
  { id: "2", lotNumber: "102", status: "ACTIVE", notes: "" },
  { id: "3", lotNumber: "103", status: "PLANNING", notes: "Hold for landscape review" },
];

export default function ProjectDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/projects">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{project.title}</h1>
            <p className="text-gray-600 mt-1">{project.address}</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline">
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
          <Button variant="outline">
            <Trash2 className="mr-2 h-4 w-4" />
            Archive
          </Button>
        </div>
      </div>

      {/* Project Overview Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-600">Budget</div>
            <div className="text-2xl font-bold mt-1">{formatCurrency(project.budget)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-600">Home Area</div>
            <div className="text-2xl font-bold mt-1">{formatNumber(project.homeAreaSqFt, 0)} SF</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-600">Start Date</div>
            <div className="text-2xl font-bold mt-1">{formatDate(project.baselineStartDate)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-600">Status</div>
            <div className="text-2xl font-bold mt-1">{project.status}</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="lots">Lots</TabsTrigger>
          <TabsTrigger value="materials" asChild>
            <Link href={`/projects/${params.id}/materials`}>Materials</Link>
          </TabsTrigger>
          <TabsTrigger value="schedule" asChild>
            <Link href={`/projects/${params.id}/schedule`}>Schedule</Link>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle>Project Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm font-medium text-gray-600">Description</div>
                <div className="mt-1">{project.description}</div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-600">Lot Dimensions</div>
                  <div className="mt-1">{project.lotWidth}' x {project.lotDepth}'</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-600">Created</div>
                  <div className="mt-1">{formatDate(project.createdAt)}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="lots">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Lots</CardTitle>
                <Button>Add Lot</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {lots.map((lot) => (
                  <div
                    key={lot.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div>
                      <div className="font-medium">Lot #{lot.lotNumber}</div>
                      <div className="text-sm text-gray-600">{lot.notes || "No notes"}</div>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {lot.status}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
