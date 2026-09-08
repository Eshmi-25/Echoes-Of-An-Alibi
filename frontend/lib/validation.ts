import { z } from "zod";

export const loginSchema = z.object({
  username_or_email: z.string().min(3),
  password: z.string().min(8)
});

export const accusationSchema = z.object({
  attacker_slug: z.string().min(1),
  thief_slug: z.string().min(1),
  motive: z.string().min(4),
  supporting1: z.string().min(1),
  supporting2: z.string().min(1),
  explanation: z.string().min(10)
});
