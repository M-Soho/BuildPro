import { z } from "zod";

export enum ReportType {
  PROGRESS = "PROGRESS",
  BUDGET_VS_ACTUAL = "BUDGET_VS_ACTUAL",
  TAKEOFF_SUMMARY = "TAKEOFF_SUMMARY",
  OM_BINDER = "OM_BINDER",
}

export enum ReportStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
}

export enum ReportFormat {
  PDF = "PDF",
  CSV = "CSV",
  XLSX = "XLSX",
}

export const ReportSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  projectId: z.string().uuid(),
  type: z.nativeEnum(ReportType),
  format: z.nativeEnum(ReportFormat),
  status: z.nativeEnum(ReportStatus),
  downloadUrl: z.string().nullable(),
  errorMessage: z.string().nullable(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export type Report = z.infer<typeof ReportSchema>;
