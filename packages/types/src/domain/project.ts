import { z } from "zod";

export enum ProjectStatus {
  PLANNING = "PLANNING",
  ACTIVE = "ACTIVE",
  ON_HOLD = "ON_HOLD",
  COMPLETED = "COMPLETED",
  ARCHIVED = "ARCHIVED",
}

export const BuildProjectSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  title: z.string(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zipCode: z.string().optional(),
  status: z.nativeEnum(ProjectStatus),
  homeAreaSqFt: z.number().positive().optional(),
  budget: z.number().optional(),
  baselineStartDate: z.string().optional(),
  baselineEndDate: z.string().optional(),
  actualStartDate: z.string().optional(),
  actualEndDate: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
  deletedAt: z.string().nullable(),
});

export const LotSchema = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid(),
  lotNumber: z.string(),
  address: z.string().optional(),
  areaSqFt: z.number().positive().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export type BuildProject = z.infer<typeof BuildProjectSchema>;
export type Lot = z.infer<typeof LotSchema>;
