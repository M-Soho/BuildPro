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
import { Plus, Download, Eye } from "lucide-react";
import { formatDate } from "@/lib/utils";

// Mock data
const reports = [
  {
    id: "1",
    title: "Monthly Progress Report - January 2024",
    type: "PROGRESS",
    status: "COMPLETED",
    format: "PDF",
    createdAt: "2024-01-31T10:00:00Z",
    projectTitle: "Sunset Hills Phase 2",
  },
  {
    id: "2",
    title: "Budget vs Actual Q1 2024",
    type: "BUDGET_VS_ACTUAL",
    status: "COMPLETED",
    format: "PDF",
    createdAt: "2024-03-31T15:30:00Z",
    projectTitle: "Downtown Lofts",
  },
];

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-gray-600 mt-1">Generate and manage project reports</p>
        </div>
        
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Generate Report
        </Button>
      </div>

      {/* Report Types */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { title: "Progress Report", type: "PROGRESS" },
          { title: "Budget vs Actual", type: "BUDGET_VS_ACTUAL" },
          { title: "Takeoff Summary", type: "TAKEOFF_SUMMARY" },
          { title: "O&M Binder", type: "OM_BINDER" },
        ].map((reportType) => (
          <Card
            key={reportType.type}
            className="cursor-pointer hover:shadow-md transition-shadow"
          >
            <CardContent className="pt-6 text-center">
              <h3 className="font-semibold">{reportType.title}</h3>
              <Button variant="outline" size="sm" className="mt-4">
                Generate
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Reports History */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Project</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Format</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Status</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reports.map((report) => (
                <TableRow key={report.id}>
                  <TableCell className="font-medium">{report.title}</TableCell>
                  <TableCell>{report.projectTitle}</TableCell>
                  <TableCell>{report.type}</TableCell>
                  <TableCell>{report.format}</TableCell>
                  <TableCell>{formatDate(report.createdAt)}</TableCell>
                  <TableCell>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {report.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="icon">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
