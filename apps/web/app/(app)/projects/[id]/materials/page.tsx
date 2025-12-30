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
import { Plus, Upload, Download, Trash2 } from "lucide-react";
import { formatCurrency, formatNumber } from "@/lib/utils";

// Mock data
const materials = [
  {
    id: "1",
    category: "FRAMING",
    description: "2x4 Lumber - 8ft",
    quantity: 500,
    unit: "EA",
    wastageFactor: 0.1,
    totalQty: 550,
    unitCost: 8.50,
    totalCost: 4675,
  },
  {
    id: "2",
    category: "CONCRETE",
    description: "Ready Mix Concrete 3000 PSI",
    quantity: 45,
    unit: "CF",
    wastageFactor: 0.05,
    totalQty: 47.25,
    unitCost: 125,
    totalCost: 5906.25,
  },
];

export default function ProjectMaterialsPage({
  params,
}: {
  params: { id: string };
}) {
  const totalCost = materials.reduce((sum, m) => sum + m.totalCost, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Materials & Takeoff</h2>
          <p className="text-gray-600 mt-1">Manage materials and calculate quantities</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline">
            <Upload className="mr-2 h-4 w-4" />
            Import CSV
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Material
          </Button>
        </div>
      </div>

      {/* Materials Table */}
      <Card>
        <CardHeader>
          <CardTitle>Material Line Items</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Category</TableHead>
                <TableHead>Description</TableHead>
                <TableHead className="text-right">Qty</TableHead>
                <TableHead>Unit</TableHead>
                <TableHead className="text-right">Wastage</TableHead>
                <TableHead className="text-right">Total Qty</TableHead>
                <TableHead className="text-right">Unit Cost</TableHead>
                <TableHead className="text-right">Total Cost</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {materials.map((material) => (
                <TableRow key={material.id}>
                  <TableCell className="font-medium">{material.category}</TableCell>
                  <TableCell>{material.description}</TableCell>
                  <TableCell className="text-right">{formatNumber(material.quantity, 0)}</TableCell>
                  <TableCell>{material.unit}</TableCell>
                  <TableCell className="text-right">
                    {(material.wastageFactor * 100).toFixed(0)}%
                  </TableCell>
                  <TableCell className="text-right">
                    {formatNumber(material.totalQty, 2)}
                  </TableCell>
                  <TableCell className="text-right">{formatCurrency(material.unitCost)}</TableCell>
                  <TableCell className="text-right font-semibold">
                    {formatCurrency(material.totalCost)}
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Summary */}
          <div className="mt-6 flex justify-end border-t pt-4">
            <div className="space-y-2">
              <div className="flex gap-8">
                <span className="text-gray-600">Total Items:</span>
                <span className="font-semibold">{materials.length}</span>
              </div>
              <div className="flex gap-8">
                <span className="text-gray-600">Grand Total:</span>
                <span className="text-xl font-bold">{formatCurrency(totalCost)}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
