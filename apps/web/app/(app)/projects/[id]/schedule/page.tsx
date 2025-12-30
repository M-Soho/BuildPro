"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Plus } from "lucide-react";
import { formatDate } from "@/lib/utils";

// Mock data
const milestones = [
  {
    id: "1",
    phase: "FOUNDATION",
    description: "Foundation Complete",
    baselineStartDate: "2024-01-15",
    baselineEndDate: "2024-02-15",
    actualStartDate: "2024-01-15",
    actualEndDate: null,
    status: "IN_PROGRESS",
  },
  {
    id: "2",
    phase: "FRAMING",
    description: "Framing Complete",
    baselineStartDate: "2024-02-20",
    baselineEndDate: "2024-03-30",
    actualStartDate: null,
    actualEndDate: null,
    status: "PLANNED",
  },
];

export default function ProjectSchedulePage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Schedule & Milestones</h2>
          <p className="text-gray-600 mt-1">Track project timeline and phases</p>
        </div>
        
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Milestone
        </Button>
      </div>

      {/* Schedule Table */}
      <Card>
        <CardHeader>
          <CardTitle>Project Milestones</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Phase</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Baseline Start</TableHead>
                <TableHead>Baseline End</TableHead>
                <TableHead>Actual Start</TableHead>
                <TableHead>Actual End</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {milestones.map((milestone) => (
                <TableRow key={milestone.id}>
                  <TableCell className="font-medium">{milestone.phase}</TableCell>
                  <TableCell>{milestone.description}</TableCell>
                  <TableCell>{formatDate(milestone.baselineStartDate)}</TableCell>
                  <TableCell>{formatDate(milestone.baselineEndDate)}</TableCell>
                  <TableCell>
                    {milestone.actualStartDate
                      ? formatDate(milestone.actualStartDate)
                      : "-"}
                  </TableCell>
                  <TableCell>
                    {milestone.actualEndDate ? formatDate(milestone.actualEndDate) : "-"}
                  </TableCell>
                  <TableCell>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        milestone.status === "IN_PROGRESS"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {milestone.status}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Gantt Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Gantt Chart</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center bg-gray-50 border-2 border-dashed rounded-lg">
            <p className="text-gray-500">Gantt chart visualization coming soon</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
