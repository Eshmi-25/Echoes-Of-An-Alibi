"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Panel } from "@/components/ui/panel";
import { api } from "@/services/api";

const schema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(8)
});

type FormValues = z.infer<typeof schema>;

export default function RegisterPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({
    resolver: zodResolver(schema)
  });

  const onSubmit = async (values: FormValues) => {
    try {
      await api.register(values);
      toast.success("Account created. Please sign in.");
      router.push("/login");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Registration failed");
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center p-4">
      <Panel title="Create Account" className="w-full">
        <form className="space-y-3" onSubmit={handleSubmit(onSubmit)}>
          <Input placeholder="Username" {...register("username")} aria-label="Username" />
          {errors.username ? <p className="text-xs text-noir-danger">{errors.username.message}</p> : null}
          <Input placeholder="Email" {...register("email")} aria-label="Email" />
          {errors.email ? <p className="text-xs text-noir-danger">{errors.email.message}</p> : null}
          <Input placeholder="Password" type="password" {...register("password")} aria-label="Password" />
          {errors.password ? <p className="text-xs text-noir-danger">{errors.password.message}</p> : null}
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Register"}
          </Button>
        </form>
        <p className="mt-3 text-sm text-white/70">
          Already have an account? <Link href="/login" className="text-noir-amber">Sign in</Link>
        </p>
      </Panel>
    </main>
  );
}
