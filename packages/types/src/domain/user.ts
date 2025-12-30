import { z } from "zod";

export enum UserRole {
  OWNER = "OWNER",
  ADMIN = "ADMIN",
  PM = "PM",
  SUPERVISOR = "SUPERVISOR",
  ESTIMATOR = "ESTIMATOR",
  SUB = "SUB",
}

export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  firstName: z.string(),
  lastName: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export const MembershipSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  userId: z.string().uuid(),
  role: z.nativeEnum(UserRole),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export type User = z.infer<typeof UserSchema>;
export type Membership = z.infer<typeof MembershipSchema>;
