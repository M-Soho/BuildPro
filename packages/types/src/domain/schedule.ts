import { z } from "zod";

export enum MilestonePhase {
  SITEWORK = "SITEWORK",
  FOUNDATION = "FOUNDATION",
  FRAMING = "FRAMING",
  ROUGH_IN = "ROUGH_IN",
  INSULATION = "INSULATION",
  DRYWALL = "DRYWALL",
  INTERIOR_FINISH = "INTERIOR_FINISH",
  EXTERIOR_FINISH = "EXTERIOR_FINISH",
  FINAL = "FINAL",
}

export const ScheduleMilestoneSchema = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid(),
  phase: z.nativeEnum(MilestonePhase),
  description: z.string().optional(),
  baselineStartDate: z.string(),
  baselineEndDate: z.string(),
  actualStartDate: z.string().nullable(),
  actualEndDate: z.string().nullable(),
  percentComplete: z.number().min(0).max(100).default(0),
  createdAt: z.string(),
  updatedAt: z.string(),
  deletedAt: z.string().nullable(),
});

export type ScheduleMilestone = z.infer<typeof ScheduleMilestoneSchema>;

export interface ScheduleVariance {
  varianceDays: number;
  isLate: boolean;
}
