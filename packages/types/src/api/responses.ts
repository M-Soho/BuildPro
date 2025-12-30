import { z } from "zod";

export const ApiErrorSchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.record(z.any()).optional(),
  }),
});

export const ApiSuccessSchema = z.object({
  data: z.any(),
});

export type ApiError = z.infer<typeof ApiErrorSchema>;
export type ApiSuccess<T = any> = {
  data: T;
};
