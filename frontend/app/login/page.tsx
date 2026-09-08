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
import { useAuthStore } from "@/stores/auth-store";

const schema = z.object({
  username_or_email: z.string().min(3),
  password: z.string().min(8)
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const setToken = useAuthStore((s) => s.setToken);
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
      const result = await api.login(values);
      setToken(result.access_token);
      window.localStorage.setItem("echoes_token", result.access_token);
      router.push("/dashboard");
      toast.success("Welcome back, detective.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Login failed");
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center p-4">
      <Panel title="Sign In" className="w-full">
        <form className="space-y-3" onSubmit={handleSubmit(onSubmit)}>
          <Input placeholder="Username or email" {...register("username_or_email")} aria-label="Username or email" />
          {errors.username_or_email ? <p className="text-xs text-noir-danger">{errors.username_or_email.message}</p> : null}
          <Input placeholder="Password" type="password" {...register("password")} aria-label="Password" />
          {errors.password ? <p className="text-xs text-noir-danger">{errors.password.message}</p> : null}
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in..." : "Sign in"}
          </Button>
        </form>
        <p className="mt-3 text-sm text-white/70">
          Need an account? <Link href="/register" className="text-noir-amber">Register</Link>
        </p>
      </Panel>
    </main>
  );
}
