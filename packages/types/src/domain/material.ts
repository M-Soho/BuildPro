import { z } from "zod";

export enum MaterialCategory {
  FRAMING = "FRAMING",
  CONCRETE = "CONCRETE",
  ELECTRICAL = "ELECTRICAL",
  PLUMBING = "PLUMBING",
  HVAC = "HVAC",
  ROOFING = "ROOFING",
  SIDING = "SIDING",
  DRYWALL = "DRYWALL",
  FLOORING = "FLOORING",
  FIXTURES = "FIXTURES",
  OTHER = "OTHER",
}

export enum UnitOfMeasure {
  LF = "LF", // Linear Feet
  SF = "SF", // Square Feet
  CF = "CF", // Cubic Feet
  EA = "EA", // Each
  LB = "LB", // Pound
  TON = "TON",
  GAL = "GAL", // Gallon
  SQ = "SQ", // Square (100 SF)
}

export const MaterialLineItemSchema = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid(),
  category: z.nativeEnum(MaterialCategory),
  description: z.string(),
  quantity: z.number().nonnegative(),
  unit: z.nativeEnum(UnitOfMeasure),
  wastageFactor: z.number().min(0).max(1).default(0), // 0.0 to 1.0 (0% to 100%)
  totalQty: z.number().nonnegative(), // computed: quantity * (1 + wastageFactor)
  unitCost: z.number().nonnegative(),
  totalCost: z.number().nonnegative(), // computed: totalQty * unitCost
  notes: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
  deletedAt: z.string().nullable(),
});

export type MaterialLineItem = z.infer<typeof MaterialLineItemSchema>;
